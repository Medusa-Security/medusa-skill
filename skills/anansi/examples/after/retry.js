function debounce(fn, wait) {
  let timer = null;
  return function (...args) {
    // Every new call resets the clock; fn only fires once things go quiet.
    clearTimeout(timer);
    // Arrow function, so `this` is whatever the wrapper was called on.
    timer = setTimeout(() => fn.apply(this, args), wait);
  };
}

// attempts is the total number of tries, not the number of *re*tries.
function retry(fn, attempts, delayMs) {
  return new Promise((resolve, reject) => {
    const attempt = (n) => {
      fn().then(resolve).catch((err) => {
        // Out of attempts: surface the last error, not the first one.
        if (n >= attempts) return reject(err);
        // Linear backoff (delay * n): polite knocking, not a battering ram.
        setTimeout(() => attempt(n + 1), delayMs * n);
      });
    };
    attempt(1);
  });
}

module.exports = { debounce, retry };
