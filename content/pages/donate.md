---
title: Donate
date: '2017-05-13T02:54:41'
slug: donate
---

[Patreon](https://www.patreon.com/platypus1917) / [Paypal](https://www.paypal.me/platypusfunds/) Donation

OR

**Platypus Membership Payment**

Trimester MembershipNon-USA Trimester $41.96 ($40+ $1.96)QuarterTwo Trimesters $82.72 ($80+ $2.72)Yearly Membership - 120 (+ 3.88 Paypal Free)Yearly Membership - 120 (+ 3.88 Paypal Free)

**Other Amount:**

**Payment Reference::**

jQuery(document).ready(function($) {
$(".wp\_accept\_pp\_button\_form\_classic").submit(function(e){
var form\_obj = $(this);
var other\_amt = form\_obj.find("input[name=other\_amount]").val();
if (!isNaN(other\_amt) && other\_amt.length > 0){
options\_val = other\_amt;
//insert the amount field in the form with the custom amount
$("<input>").attr({
type: "hidden",
id: "amount",
name: "amount",
value: options\_val
}).appendTo(form\_obj);
}
return;
});
});
