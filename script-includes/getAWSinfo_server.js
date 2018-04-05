/*
 * MyFavoritesAjax script include Description - sample AJAX processor returning multiple value pairs
 */
var TerraformAWSAccountQuery = Class.create();
TerraformAWSAccountQuery.prototype = Object.extendsObject(AbstractAjaxProcessor, {

	 /*
	 * method available to client scripts call using:
	 * var awsAccountValues = new GlideAjax("TerraformAWSAccountQuery");
	 * awsAccountValues.addParam("sysparm_name","getAWSAccountInfo");
	 */
	getAWSAccountInfo: function() { // build new response xml element for result
        var result = { favorites: [], message: '' };
        result.message = "returning all favorites";
        result.favorites.push({ 'key': 'color', 'value': 'blue'});
        result.favorites.push({ 'key': 'beer', 'value': 'lager'});
        result.favorites.push({ 'key': 'pet', 'value': 'dog'});
        return new JSON().encode(result); // Encodes result object as JSON string and pipes it to the XML answer
      },
      type : "TerraformAWSAccountQuery"
   });
