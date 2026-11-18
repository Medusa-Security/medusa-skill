function debounce(fn, wait) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), wait);
  };
}

function retry(fn, attempts, delayMs) {
  return new Promise((resolve, reject) => {
    const attempt = (n) => {
      fn().then(resolve).catch((err) => {
        if (n >= attempts) return reject(err);
        setTimeout(() => attempt(n + 1), delayMs * n);
      });
    };
    attempt(1);
  });
}

module.exports = { debounce, retry };
