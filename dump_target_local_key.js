// Read only the local key for one user-selected device from live SDK objects.
// Device ID is injected as a JSON string literal by get_local_key.py.
send({ event: "java_bridge_loaded", androidVersion: Java.androidVersion });

// The device page should already be open so the application class loader is
// initialized. performNow avoids Frida's deferred class-loader readiness path.
Java.performNow(function () {
  const targetId = __DEVICE_ID_JSON__;
  const classes = [
    "com.thingclips.smart.interior.device.bean.DeviceRespBean",
    "com.thingclips.smart.sdk.bean.DeviceBean",
  ];
  const emitted = {};

  function inspect(name, object) {
    try {
      const id = object.getDevId();
      if (id === null || id.toString() !== targetId || emitted[name]) return;
      const localKey = object.getLocalKey();
      if (localKey !== null && localKey.toString().length > 0) {
        emitted[name] = true;
        send({
          event: "target_local_key",
          className: name,
          deviceId: targetId,
          localKey: localKey.toString(),
        });
      } else {
        send({
          event: "target_found_key_empty",
          className: name,
          deviceId: targetId,
        });
      }
    } catch (_) {}
  }

  classes.forEach(function (name) {
    try {
      const klass = Java.use(name);
      const getter = klass.getLocalKey.overload();
      getter.implementation = function () {
        const result = getter.call(this);
        inspect(name, this);
        return result;
      };
      Java.choose(name, {
        onMatch: function (object) {
          inspect(name, object);
        },
        onComplete: function () {
          send({
            event: "scan_complete",
            className: name,
            targetFound: !!emitted[name],
          });
        },
      });
    } catch (error) {
      send({ event: "hook_error", className: name, error: String(error) });
    }
  });
});
