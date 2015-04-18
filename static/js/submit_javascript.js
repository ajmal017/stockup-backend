
function ccccccccccc() {
var algo_v = document.getElementById("algo_v").value;
var algo_id = document.getElementById("algo_id").value;
var algo_name = document.getElementById("algo_name").value;
var stock_id = document.getElementById("stock_id").value;
var user_id = document.getElementById("user_id").value;
var price_type = document.getElementById("price_type").value;
var trade_method = document.getElementById("trade_method").value;
var period = document.getElementById("period").value;
var primary_condition = document.getElementById("primary_condition").value;
var volume = document.getElementById("volume").value;
var condition_name = document.getElementById("condition_name").value;
var n = document.getElementById("n").value;
var m = document.getElementById("m").value;
var m1 = document.getElementById("m1").value;
var window = document.getElementById("window").value;
//if (validation()) // Calling validation function
{
var jjjjj = {"_id":{ "algo_v": algo_v, "algo_id": algo_id },
"algo_name":algo_name,"stock_id":stock_id,"user_id":user_id,"price_type":price_type,"trade_method":trade_method,"period":period,
"primary_condition":"kdj_condition","volume":volume,"conditions":{"kdj_condition":{"n":n,"m":m,"m1":m1,"window":window}}};
	
var algojson = JSON.stringify(jjjjj)
alert(condition_name);
$.post( "/algo/upload/",algojson, function( data ) {
   alert('success');
  //$( ".result" ).html( data );
});
//document.getElementById("algo").submit(); //form submission
//alert(" Name : " + name + " \n Email : " + email + " \n Form Id : " + document.getElementById("form_id").getAttribute("id") + "\n\n Form Submitted Successfully......");
}
}

// Submit form with class function.
function submit_stocklist() {
	$.getJSON(
		"/stock-list/",
		function(data){
					//alert(data)
					//var obj = $.parseJSON(data);
					var tt="";
					$.each(data,function(k,v){
							//alert(v)
							tt += k + "£º" + v + "<br/>";
						
					})
		//alert(tt)
		$("body").html(tt);
});
}

// Submit form with HTML <form> tag function.
function submit_by_tag() {
var name = document.getElementById("name").value;
var email = document.getElementById("email").value;
if (validation()) // Calling validation function
{
var x = document.getElementsByTagName("form");
x[0].submit(); //form submission
alert(" Name : " + name + " \n Email : " + email + " \n Form Tag : <form>\n\n Form Submitted Successfully......");
}
}

// Name and Email validation Function.
function validation() {
var name = document.getElementById("name").value;
var email = document.getElementById("email").value;
var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
if (name === '' || email === '') {
alert("Please fill all fields...!!!!!!");
return false;
} else if (!(email).match(emailReg)) {
alert("Invalid Email...!!!!!!");
return false;
} else {
return true;
}
}
