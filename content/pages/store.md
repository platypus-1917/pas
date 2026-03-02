---
title: Store
date: '2019-10-02T14:03:29'
slug: store
---

function createClass(name,rules){
var style = document.createElement('style');
style.type = 'text/css';
document.getElementsByTagName('head')[0].appendChild(style);
if(!(style.sheet||{}).insertRule)
(style.styleSheet || style.sheet).addRule(name, rules);
else
style.sheet.insertRule(name+'{'+rules+'}',0);
}
createClass('#static-ec-store-container','display:none;');

The store is closed for maintenance

 .ec-store \* {
transition: none !important;
}

var EcStaticPageUtils = (function () {
function isEmpty(str) {
return (!str || 0 === str.length);
}
function isNotEmpty(str) {
return !isEmpty(str);
}
function findFirstNotEmpty(urlArray) {
if (!urlArray) {
return "";
}
for (var i = 0; i < urlArray.length; i++) {
if (isNotEmpty(urlArray[i])) {
return urlArray[i];
}
}
return "";
}
return {
findFirstNotEmpty: function(urlArray) { return findFirstNotEmpty(urlArray); },
isEmpty: function(str) { return isEmpty(str); },
isNotEmpty: function(str) { return isNotEmpty(str); }
};
}) ();
var LanguageUtils = (function () {
function isEnglish(languageCode) {
return languageCode === "en";
}
function isItalian(languageCode) {
return languageCode === "it";
}
function isGerman(languageCode) {
return languageCode === "de";
}
function isPolish(languageCode) {
return languageCode === "pl";
}
function isFrench(languageCode) {
return languageCode === "fr";
}
function isSpanish(languageCode) {
return languageCode === "es";
}
function isBulgarian(languageCode) {
return languageCode === "bg";
}
function isCroatian(languageCode) {
return languageCode === "hr";
}
function isCzech(languageCode) {
return languageCode === "cs";
}
function isDanish(languageCode) {
return languageCode === "da";
}
function isEstonian(languageCode) {
return languageCode === "et";
}
function isFinnish(languageCode) {
return languageCode === "fi";
}
function isGreek(languageCode) {
return languageCode === "el";
}
function isHungarian(languageCode) {
return languageCode === "hu";
}
function isLatvian(languageCode) {
return languageCode === "lv";
}
function isLithuanian(languageCode) {
return languageCode === "lt";
}
function isDutch(languageCode) {
return languageCode === "nl";
}
function isPortuguese(languageCode) {
return languageCode === "pt";
}
function isRomanian(languageCode) {
return languageCode === "ro";
}
function isSlovak(languageCode) {
return languageCode === "sk";
}
function isSlovenian(languageCode) {
return languageCode === "sl";
}
function isSwedish(languageCode) {
return languageCode === "sv";
}
return {
isEnglish: function(language) { return isEnglish(language); },
isItalian: function(language) { return isItalian(language); },
isGerman: function(language) { return isGerman(language); },
isPolish: function(language) { return isPolish(language); },
isFrench: function(language) { return isFrench(language); },
isSpanish: function(language) { return isSpanish(language); },
isBulgarian: function(language) { return isBulgarian(language); },
isCroatian: function(language) { return isCroatian(language); },
isCzech: function(language) { return isCzech(language); },
isDanish: function(language) { return isDanish(language); },
isEstonian: function(language) { return isEstonian(language); },
isFinnish: function(language) { return isFinnish(language); },
isGreek: function(language) { return isGreek(language); },
isHungarian: function(language) { return isHungarian(language); },
isLatvian: function(language) { return isLatvian(language); },
isLithuanian: function(language) { return isLithuanian(language); },
isDutch: function(language) { return isDutch(language); },
isPortuguese: function(language) { return isPortuguese(language); },
isRomanian: function(language) { return isRomanian(language); },
isSlovak: function(language) { return isSlovak(language); },
isSlovenian: function(language) { return isSlovenian(language); },
isSwedish: function(language) { return isSwedish(language); }
};
}) ();
(function processProductPictures() {
var productsPicturesData = buildProductPicturesData();
var lastWidth = document.body.clientWidth;
function buildProductPicturesData() {
return [ ];
}
function addSrcSetAttribute(element, retinaThumbnailUrl) {
if (!element) {
return;
}
var thumbnailUrl = element.getAttribute('src');
var srcSetAttribute;
if (EcStaticPageUtils.isNotEmpty(thumbnailUrl) && EcStaticPageUtils.isNotEmpty(retinaThumbnailUrl)) {
srcSetAttribute = thumbnailUrl + " 1x, " + retinaThumbnailUrl + " 2x";
} else if (EcStaticPageUtils.isNotEmpty(thumbnailUrl)) {
srcSetAttribute = thumbnailUrl + " 1x";
} else if (EcStaticPageUtils.isNotEmpty(retinaThumbnailUrl)) {
srcSetAttribute = retinaThumbnailUrl + " 2x";
}
if (srcSetAttribute) {
var lazyLoadingEnabled = "false";
if (lazyLoadingEnabled === "true") {
element.setAttribute("data-srcset", srcSetAttribute);
} else {
element.setAttribute("srcset", srcSetAttribute);
}
}
}
function setBackgroundImageStyle(element, thumbnailUrl, retinaThumbnailUrl, borderInfo) {
if (!element || !borderInfo || (EcStaticPageUtils.isEmpty(thumbnailUrl) && EcStaticPageUtils.isEmpty(retinaThumbnailUrl))) {
return;
}
var notEmptyRetinaThumbnailUrl = retinaThumbnailUrl;
if (EcStaticPageUtils.isEmpty(retinaThumbnailUrl)) {
notEmptyRetinaThumbnailUrl = thumbnailUrl;
}
element.setAttribute("style", "background-image: url("
+ thumbnailUrl
+ "); background-image: -webkit-image-set(url("
+ thumbnailUrl
+ ") 1x, url("
+ notEmptyRetinaThumbnailUrl
+ ") 2x); background-image: -moz-image-set(url("
+ thumbnailUrl
+ ") 1x, url("
+ notEmptyRetinaThumbnailUrl
+ ") 2x); background-image: -o-image-set(url("
+ thumbnailUrl
+ ") 1x, url("
+ notEmptyRetinaThumbnailUrl
+ ") 2x); background-image: -ms-image-set(url("
+ thumbnailUrl
+ ") 1x, url("
+ notEmptyRetinaThumbnailUrl
+ ") 2x);"
+ backgroundColor(borderInfo));
}
function backgroundColor(borderInfo) {
if (borderInfo.alpha == 0) {
return "";
}
return " background-color: rgba" + "(" + borderInfo.red + ", "
+ borderInfo.green
+ ", " + borderInfo.blue + ", 1)"
}
function hdProductImage(pictureModel) {
var imageSize = "MEDIUM";
var browserWidth = document.body.clientWidth;
switch (imageSize) {
case "SMALL":
if (browserWidth < 520) {
return hdThumbnailUrl(pictureModel);
}
return thumbnailUrl(pictureModel);
case "MEDIUM":
return hdThumbnailUrl(pictureModel);
case "LARGE":
return pictureUrl(pictureModel);
}
}
function productImage(pictureModel) {
var imageSize = "MEDIUM";
switch (imageSize) {
case "SMALL":
case "MEDIUM":
return thumbnailUrl(pictureModel);
case "LARGE":
return hdThumbnailUrl(pictureModel);
}
}
function hdThumbnailUrl(pictureModel) {
var urls = [
pictureModel.hdThumbnailUrl,
pictureModel.thumbnailUrl,
pictureModel.pictureUrl,
pictureModel.originalImageUrl
];
return EcStaticPageUtils.findFirstNotEmpty(urls);
}
function thumbnailUrl(pictureModel) {
var urls = [
pictureModel.thumbnailUrl,
pictureModel.hdThumbnailUrl,
pictureModel.pictureUrl,
pictureModel.originalImageUrl
];
return EcStaticPageUtils.findFirstNotEmpty(urls);
}
function pictureUrl(pictureModel) {
var urls = [
pictureModel.pictureUrl,
pictureModel.hdThumbnailUrl,
pictureModel.originalImageUrl,
pictureModel.thumbnailUrl
];
return EcStaticPageUtils.findFirstNotEmpty(urls);
}
function process() {
if (window.ec && window.ec.storefront && window.ec.storefront.staticPages && window.ec.storefront.staticPages.staticContainerID) {
var staticContainer = document.querySelector('#' + window.ec.storefront.staticPages.staticContainerID);
if (staticContainer == null) {
window.removeEventListener("resize", onResize);
return;
}
}
var pictureElements = document.querySelectorAll('.grid-product\_\_image');
if (productsPicturesData.length !== pictureElements.length) {
return;
}
productsPicturesData.forEach(function (item, i) {
var imageWrapper = document.querySelector(".grid-product\_\_image[data-product-id='" + item.id + "']");
var pictureElement = imageWrapper.querySelector('.grid-product\_\_picture');
var additionalPictureElement = imageWrapper.querySelector('.grid-product\_\_picture-additional');
addSrcSetAttribute(pictureElement, hdProductImage(item));
if (additionalPictureElement != null && item.additionalImage != undefined) {
setBackgroundImageStyle(additionalPictureElement, productImage(item.additionalImage), hdProductImage(item.additionalImage), item.additionalImage.borderInfo);
}
});
}
function onResize() {
if (document.body.clientWidth !== lastWidth) {
lastWidth = document.body.clientWidth;
process();
}
}
window.addEventListener("resize", onResize);
process();
})();
(function processRibbonColor() {
function getColorValues(color) {
if (!color)
return;
if (color.toLowerCase() === 'transparent')
return [0, 0, 0, 0];
if (color[0] === '#') {
if (color.length == 6)
return;
if (color.length < 7) {
var r = color[1],
g = color[2],
b = color[3],
a = color[4];
color = '#' + r + r + g + g + b + b + (color.length > 4 ? a + a : '');
}
return [
parseInt(color.substr(1, 2), 16),
parseInt(color.substr(3, 2), 16),
parseInt(color.substr(5, 2), 16),
color.length > 7 ? parseInt(color.substr(7, 2), 16)/255 : 1
];
}
if (color.indexOf('rgb') === -1) {
var tmp = document.body.appendChild(document.createElement('fictum'));
var flag = 'rgb(1, 2, 3)';
tmp.style.color = flag;
if (tmp.style.color !== flag)
return;
tmp.style.color = color;
if (tmp.style.color === flag || tmp.style.color === '')
return;
color = getComputedStyle(tmp).color;
document.body.removeChild(tmp);
}
if (color.indexOf('rgb') === 0) {
if (color.indexOf('rgba') === -1)
color += ',1';
return color.match(/[\.\d]+/g).map(function (a) {
return +a
});
}
}
function isColorDark(color) {
var c = getColorValues(color);
var hsp = Math.sqrt(
0.299 \* (c[0] \* c[0]) +
0.587 \* (c[1] \* c[1]) +
0.114 \* (c[2] \* c[2])
);
return !!(hsp <= 200);
}
function process() {
var ribbonElements = document.querySelectorAll('.grid-product\_\_label');
if (ribbonElements) {
ribbonElements.forEach(function (item, i) {
var ribbonElement = ribbonElements[i].querySelector('.ec-label');
var color = ribbonElement.style.color;
if (color) {
ribbonElement.classList.toggle('label--inversed', !isColorDark(color));
}
});
}
}
process();
})();
(function processCategoryPictures() {
var categoryPicturesData = buildCategoryPicturesData();
var lastWidth = document.body.clientWidth;
var sizeBorder = 400;
function buildCategoryPicturesData() {
return [
];
}
function categoryImage(pictureModel) {
var imageSize = "MEDIUM";
switch (imageSize) {
case "SMALL":
case "MEDIUM":
return thumbnailUrl(pictureModel);
case "LARGE":
return hdThumbnailUrl(pictureModel);
}
}
function hdCategoryImage(pictureModel) {
var imageSize = "MEDIUM";
var browserWidth = document.body.clientWidth;
switch (imageSize) {
case "SMALL":
if (browserWidth < 520) {
return hdThumbnailUrl(pictureModel);
}
return thumbnailUrl(pictureModel);
case "MEDIUM":
return hdThumbnailUrl(pictureModel);
case "LARGE":
if (browserWidth < 1060) {
return hdThumbnailUrl(pictureModel);
}
return mainImageUrl(pictureModel)
}
}
function hdThumbnailUrl(pictureModel) {
var urls = [
pictureModel.hdThumbnailUrl,
pictureModel.mainImageUrl,
pictureModel.originalImageUrl,
pictureModel.pictureUrl
];
return EcStaticPageUtils.findFirstNotEmpty(urls);
}
function mainImageUrl(pictureModel) {
var urls = [
pictureModel.mainImageUrl,
pictureModel.originalImageUrl,
pictureModel.pictureUrl
];
return EcStaticPageUtils.findFirstNotEmpty(urls);
}
function thumbnailUrl(pictureModel) {
if (pictureModel.pictureWidth < sizeBorder && pictureModel.pictureHeight < sizeBorder) {
return hdThumbnailUrl(pictureModel);
} else {
return pictureModel.pictureUrl;
}
}
function process() {
var categoryImageElements = document.querySelectorAll('.grid-category\_\_image');
if (categoryImageElements.length !== categoryPicturesData.length) {
return;
}
categoryPicturesData.forEach(function (item, i) {
var categoryImageUrl = categoryImage(item);
var hdCategoryImageUrl = hdCategoryImage(item);
var categoryPictureElements = categoryImageElements[i].querySelectorAll('.grid-category\_\_picture-img');
categoryPictureElements.forEach(function (element, j) {
addSrcSetAttribute(element, categoryImageUrl, hdCategoryImageUrl);
});
});
}
function addSrcSetAttribute(element, thumbnailUrl, retinaThumbnailUrl) {
if (!element) {
return;
}
var srcSetAttribute;
if (EcStaticPageUtils.isNotEmpty(thumbnailUrl) && EcStaticPageUtils.isNotEmpty(retinaThumbnailUrl)) {
srcSetAttribute = thumbnailUrl + " 1x, " + retinaThumbnailUrl + " 2x";
} else if (EcStaticPageUtils.isNotEmpty(thumbnailUrl)) {
srcSetAttribute = thumbnailUrl + " 1x";
} else if (EcStaticPageUtils.isNotEmpty(retinaThumbnailUrl)) {
srcSetAttribute = retinaThumbnailUrl + " 2x";
}
if (srcSetAttribute) {
var lazyLoadingEnabled = "false";
if (lazyLoadingEnabled === "true") {
element.setAttribute("data-srcset", srcSetAttribute);
} else {
element.setAttribute("srcset", srcSetAttribute);
}
}
}
function onResize() {
if (document.body.clientWidth !== lastWidth) {
lastWidth = document.body.clientWidth;
process();
}
}
window.addEventListener("resize", onResize);
process();
})();
(function() {
window.ec = window.ec || {};
if (window.ec.static\_category\_evaluated === true) {
return;
}
window.ec.static\_category\_evaluated = true;
var Grid = function() {
var params = {
productListImageSize : "MEDIUM",
categoryImageSize : "MEDIUM",
productCellSpacing : "",
categoryCellSpacing : ""
};
var settings = {
productBreakpoints: {
LARGE : [0, 680, 1060, 1440, 10000],
MEDIUM : [0, 260, 680, 1060, 1370, 1700, 10000],
SMALL : [0, 260, 520, 680, 870, 1060, 1280, 1450, 1750, 10000]
},
categoryBreakpoints: {
LARGE : [0, 680, 1060, 1440, 10000],
MEDIUM : [0, 480, 680, 1060, 1370, 1700, 10000],
SMALL : [0, 390, 520, 680, 870, 1060, 1280, 1450, 1750, 10000]
}
};
function setAttributes(grids, breakpoints) {
if (!grids) {
return;
}
grids.forEach(function (grid) {
var w = grid.offsetWidth;
var columnCount = 0;
for (var i = 1; i <= breakpoints.length; i++) {
if (w < Math.ceil(breakpoints[i])) {
if (i !== columnCount) {
columnCount = i;
grid.setAttribute('data-cols', i);
}
break;
}
}
});
}
function checkProductGridsLayout() {
var productGrids = document.querySelectorAll('.grid\_\_products');
var productBreakpoints = settings.productBreakpoints[params.productListImageSize];
setAttributes(productGrids, productBreakpoints);
}
function checkCategoryGridsLayout() {
var categoryGrids = document.querySelectorAll('.grid\_\_categories');
var categoryBreakpoints = settings.categoryBreakpoints[params.categoryImageSize];
setAttributes(categoryGrids, categoryBreakpoints);
}
function checkLayout() {
checkProductGridsLayout();
checkCategoryGridsLayout();
}
function setCellInterval(p, c) {
var style = document.getElementById('customCss') || document.createElement('div');
style.id = 'customCss';
document.body.appendChild(style);
var css = '';
if (+p == p && p != "" ) {
p = +p;
css += '.ec-size .ec-store .grid\_\_products { margin-left: -' + Math.max(0, p/2 - .4) + 'px; margin-right: -' + p/2 + 'px; }';
css += '.ec-size .ec-store .grid\_\_products .grid-product\_\_wrap { padding: ' + p/2 + 'px; }';
css += '.ec-size:not(.ec-size--s) .ec-store .grid\_\_products { margin-left: -' + Math.max(0, Math.min(16, p) / 2 - .4) + 'px; margin-right: -' + Math.min(16, p) / 2 + 'px; }';
css += '.ec-size:not(.ec-size--s) .ec-store .grid\_\_products .grid-product\_\_wrap { padding: ' + Math.min(16, p) / 2 + 'px; }';
}
if (+c == c && c != "") {
c = +c;
css += '.ec-size .ec-store .grid\_\_categories { margin-left: -' + Math.max(0, c/2 - .4) + 'px; margin-right: -' + c/2 + 'px; }';
css += '.ec-size .ec-store .grid-category\_\_wrap { padding: ' + c/2 + 'px; }';
css += '.ec-size:not(.ec-size--s) .ec-store .grid\_\_categories { margin-left: -' + Math.max(0, Math.min(16, c) / 2 - .4) + 'px; margin-right: -' + Math.min(16, c) / 2 + 'px; }';
css += '.ec-size:not(.ec-size--s) .ec-store .grid\_\_categories .grid-category\_\_wrap { padding: ' + Math.min(16, c) / 2 + 'px; }';
}
style.innerHTML = '
<style>' + css + '</style>
<p>';
}
function init() {
setCellInterval(params.productCellSpacing, params.categoryCellSpacing);
checkLayout();
window.addEventListener('resize', function() {
checkLayout();
});
}
init();
};
var ecwidContainer = document.querySelector('.static-content .ec-size');
var breakpoints = {
320: 'ec-size--xxs',
414: 'ec-size--xs',
480: 'ec-size--s',
768: 'ec-size--m',
1024: 'ec-size--l',
1100: 'ec-size--xl',
1440: 'ec-size--xxl'
};
function onResize() {
var w = ecwidContainer.offsetWidth;
for (var i in breakpoints) {
if (w >= i) {
ecwidContainer.classList.add(breakpoints[i]);
}
else {
ecwidContainer.classList.remove(breakpoints[i]);
}
}
}
onResize();
window.addEventListener('load', onResize);
window.addEventListener('resize', onResize);
var links = document.querySelectorAll(".static-content a");
for (var i = 0; i < links.length; i++) {
var link = links[i];
link.addEventListener('click',function(){
document.querySelector('.ec-static-container').classList.add("static-content\_\_wait");
})
}
var grid = new Grid();
})();

if (typeof jQuery !== undefined && jQuery.mobile) { jQuery.mobile.hashListeningEnabled = false; jQuery.mobile.pushStateEnabled=false; }

xProductBrowser("id=ecwid-store-7091170","views=grid(20,3) list(60) table(60)","default\_page=");
