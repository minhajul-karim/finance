// When the page is loaded

$(document).ready(function() {

    $name = "";

    // When user presses any key in username field
    $("#usr").on("change keyup paste", function() {
    	$name = $("#usr").val();
    });

	/************* validation for other registration fields ***********/

	$("#reg_form").validate({
		rules: {
			username: {
				required: true,
				minlength: 1
			},

			password: {
				required: true,
				minlength: 5,
				uppercase: true,
				numbers: true,
				specialChars: true
			},

			confirmation: {
				required: true,
				minlength: 5,
				equalTo: "#pwd1"
			}
		},

		messages: {
			username: {
				required: "Please enter username",
				minlength: "Username must contain at least one character"
			},

			password: {
				required: "Please enter a password",
				minlength: "Password must contain at least 5 characters",
				uppercase: "Must contain uppercase",
				numbers: "Must have a number",
				specialChars: "Must have a special char"
			},

			confirmation: {
				required: "Please again enter your password",
				minlength: "Password must contain at least 5 characters",
				equalTo: "Both passwords must match"
			}
		},

		submitHandler: function(form) {

			$.ajax({

				dataType: "json",
				url: '/check',
	        	data: {
	        		username: $name
	    		},

	    		type: 'GET',

	    		// If ajax call ends successfully
	        	success: function(data) {

	        		if (data) {

	        			// Notify user that username is available
	        			$("#availability").html("Username avaialable").addClass("available");
	        			$("#availability").removeClass("notAvailable");
	        			form.submit();
	        		}
	        		else {

	        			// Notify user that username is available
	        			$("#availability").html("Username not avaialable").addClass("notAvailable");
	        			$("#availability").removeClass("available");
	        		}
	    		}

		    }); // ajax ends
		}

	});

	/***** Add new methods to registration from validation *******/

	// Method to check uppercase letters
	$.validator.addMethod("uppercase", function(value) {
		return /[A-Z]+/.test(value);
	});

	// Method to check digits
	$.validator.addMethod("numbers", function(value) {
		return /[0-9]+/.test(value);
	});

	// Method to check special characters
	$.validator.addMethod("specialChars", function(value) {
		return /\W/.test(value);
	});


	/******** Login form validation **********/

	$("#login_form").validate({
		rules: {
			username: {
				required: true
			},

			password: {
				required: true
			}
		},

		messages: {
			username: {
				required: "Please enter your username"
			},

			password: {
				required: "Please enter your password"
			}
		}

	});

	/*********** Quote validation *************/
	$("#quote_form").validate({
		rules: {
			symbol: {
				required: true
			}
		},

		messages: {
			symbol: {
				required: "Please enter a symbol"
			}
		}

	});


	// When user submits the registration button of index page
	$('[name="buy_button"]').on('click', function() {

		// Grab the immediate parent of the button
		$td = $(this).parent();

		// Grab the immediate parent of $td
		$tr = $td.parent();

		// Grab the symbol of that row
		$symbol = $tr.children('.symbol_row').children('.symbol').text();

		// ajax starts

		$.ajax({
		    data: {
		        sym: $symbol
		    },
		    type: "GET",
		    dataType: "json",
		    url: "/save_symbol_in_session",
		    success: function(data) {
		        if (data) {
		    		window.location.assign("/buythis");
		    	}
		    	else {
		    		alert("Sorry! Something went wrong!");
		    		window.location.assign("/");
		    	}
		    }

		});

		// ajax ends

	}); // click function ends


	// When user clicks the sell button of index page
	$('[name="sell_button"]').on('click', function() {

		// Grab the immediate parent of the button
		$td = $(this).parent();

		// Grab the immediate parent of $td
		$tr = $td.parent();

		// Grab the symbol of that row
		$symbol = $tr.children('.symbol_row').children('.symbol').text();

		// ajax starts

		$.ajax({
		    data: {
		        sym: $symbol
		    },
		    type: "GET",
		    dataType: "json",
		    url: "/save_symbol_in_session",
		    success: function(data) {
		        if (data) {
		    		window.location.assign("/sellthis");
		    	}
		    	else {
		    		alert("Sorry! Something went wrong!");
		    		window.location.assign("/");
		    	}
		    }

		});

		// ajax ends

	}); // click function ends

}); // doc ends