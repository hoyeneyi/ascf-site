/* Google Analytics 4 ------------------------------------------------
   Replace G-XXXXXXXXXX below with the real Measurement ID from
   analytics.google.com. Until then nothing is sent and the site
   works normally.
------------------------------------------------------------------ */
(function () {
  var GA_ID = 'G-XXXXXXXXXX';
  if (GA_ID.indexOf('XXXX') > -1) { return; }
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', GA_ID);
})();
