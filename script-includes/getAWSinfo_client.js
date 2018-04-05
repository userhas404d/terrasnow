//reference: https://community.servicenow.com/community?id=community_question&sys_id=b0ff4ba5dbdcdbc01dcaf3231f961989
// new GlideAjax object referencing name of AJAX script include
var ga = new GlideAjax("TerraformAWSAccountQuery");
// add name parameter to define which function we want to call
// method name in script include will be getFavorites
ga.addParam("sysparm_name", "getAWSAccountInfo");
// submit request to server, call ajaxResponse function with server response
ga.getXMLWait();
var resp = ga.getAnswer();
resp = JSON.parse(resp); // Parse the JSON string
alert(resp.message);
for (var i = 0; i < resp.favorites.length; i++) {

       alert(resp.favorites[i].key + ': ' + resp.favorites[i].value);

}
