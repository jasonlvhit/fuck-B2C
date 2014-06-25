// JavaScript Document
function checkitemform() {
	if (document.form1.name.value === "") {
		window.alert("请输入商品名称！");
		document.form1.name.focus();
		return false;
	}
	if (document.form1.price.value == "") {
		window.alert("请输入商品价格！");
		document.form1.price.focus();
		return false;
	}
	if (document.form1.storage.value == "") {
		window.alert("请输入商品库存量！");
		document.form1.storage.focus();
		return false;
	}
	if (document.form1.discount.value == "") {
		window.alert("请输入商品折扣！");
		document.form1.discount.focus();
		return false;
	} else {
		window.location.href = "item_list.html";
	}
}

function checkregform() {
	if (document.form1.email.value === "") {
		window.alert("请输入有效的邮箱地址！");
		document.form1.name.focus();
		return false;
	}
	if (document.form1.password.value == "") {
		window.alert("请输入密码！");
		document.form1.password.focus();
		return false;
	}
	if (document.form1.passwordConfirm.value == "") {
		window.alert("请再次输入密码！");
		document.form1.passwordConfirm.focus();
		return false;
	} else {
		window.location.href = "home.html";
	}
}

function checkcategoryform() {
	if (document.form1.name.value === "") {
		window.alert("请输入目录名称！");
		document.form1.name.focus();
		return false;
	} else {
		window.location.href = "category_list.html";
	}

}

function checkstorageform() {
	if (document.form1.storage.value === "") {
		window.alert("请输入库存量！");
		document.form1.storage.focus();
		return false;
	} else {
		window.location.href = "storage_list.html";
	}

}

function checkpriceform() {
	if (document.form1.price.value === "") {
		window.alert("请输入价格！");
		document.form1.price.focus();
		return false;
	}
	if (document.form1.discount.value === "") {
		window.alert("请输入库存量！");
		document.form1.discount.focus();
		return false;
	} else {
		window.location.href = "price_list.html";
	}

}

function checkloginform() {
	if (document.form1.name.value === "") {
		window.alert("请输入用户名！");
		document.form1.name.focus();
		return false;
	}
	if (document.form1.password.value === "") {
		window.alert("请输入密码！");
		document.form1.password.focus();
		return false;
	} else {
		window.location.href = "category_list.html";
	}

}

function checkusersetform() {

	if (document.form1.credit.value === "") {
		window.alert("请输入积分下限！");
		document.form1.credit.focus();
		return false;
	}
	if (document.form1.ratio.value === "") {
		window.alert("请输入积分比例！");
		document.form1.ratio.focus();
		return false;
	} else {
		window.location.href = "user_admin.html";
	}
}

function checkordercheck() {
	window.alert("审核成功！");
	window.location.href = "order_list_refresh.html";
}

function checkorderselect() {
	var k = 0;
	var radio_checked = false;
	radios = document.getElementsByName('order_id');
	for (i = 0; i < radios.length ; i++) {
		if (radios[i].checked ) {
			return true
		}
	}
	window.alert("请选择订单！");
	return false;
}

function checkitemrefresh() {
	if (document.form1.name.value === "") {
		window.alert("请输入商品名称！");
		document.form1.name.focus();
		return false;
	}
	if (document.form1.price.value == "") {
		window.alert("请输入商品价格！");
		document.form1.price.focus();
		return false;
	}
	if (document.form1.storage.value == "") {
		window.alert("请输入商品库存量！");
		document.form1.storage.focus();
		return false;
	}
	if (document.form1.discount.value == "") {
		window.alert("请输入商品折扣！");
		document.form1.discount.focus();
		return false;
	} else {
		window.location.href = "item_list_refresh.html";
	}

}