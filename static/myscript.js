$(document).ready(function() {

	/************* Registration form validation ***********/

	$("#reg_form").validate({
	
		// Define rules
		rules: {

			first_name: {
				required: true
			},

			last_name: {
				required: true
			},

			email: {
				required: true,
				validEmail: true
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

		// Error Messages
		messages: {

			first_name: {
				required: "Please enter your first name"
			},

			last_name: {
				required: "Please enter your last name"
			},

			email: {
				required: "Pleaase enter a valid email address",
				validEmail: "Pleaase enter a valid email address"
			},

			password: {
				required: "Please enter new password",
				minlength: "Password must contain at least 5 characters",
				uppercase: "Password must contain uppercase",
				numbers: "Password must have a number",
				specialChars: "Password must have a special char"
			},

			confirmation: {
				required: "Please enter your password again",
				minlength: "Password must contain at least 5 characters",
				equalTo: "Both passwords must match"
			}
		},

		// Username availability check after form submission
		submitHandler: function(form) {

			$.ajax({

				dataType: "json",
				url: '/check',
				data: {
					mail: $("#mail").val()
				},

				type: 'GET',

				// If ajax call ends successfully
				success: function(data) {

					if (data) {
						
						// email is available
						$("#email_group p").html("").removeAttr("id");

						// Submit the form
						form.submit();
					}

					else {
						// Notify user that username is not available
						$("#email_group p").html("Someone is already using that email").attr("id", "emailNotAvailable");
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

	$.validator.addMethod("validEmail", function(value) {
		return /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/.test(value);
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

	/*********** Quote form validation *************/
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

	/*********** Buy form validation *************/
	$("#buy_form").validate({
		rules: {
			symbol: {
				required: true
			},

			shares: {
				required: true
			}
		},

		messages: {
			symbol: {
				required: "Please enter a symbol"
			},
			shares: {
				required: "Please enter amount of shares"
			}
		}

	});

	/*********** Sell form validation *************/
	$("#sell_form").validate({
		rules: {
			symbol: {
				required: true
			},

			shares: {
				required: true
			}
		},

		messages: {
			symbol: {
				required: "Please enter a symbol"
			},
			shares: {
				required: "Please enter amount of shares"
			}
		}

	});

	/******** Update password form validation*******/

	$("#update_password_area form").validate({
		
		rules: {
			
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
				equalTo: "#update_pwd"
			}
		},

		messages: {
			password: {
				required: "Please enter new password",
				minlength: "Password must contain at least 5 characters",
				uppercase: "Password must contain uppercase",
				numbers: "Password must have a number",
				specialChars: "Password must have a special char"
			},

			confirmation: {
				required: "Please enter your password again",
				minlength: "Password must contain at least 5 characters",
				equalTo: "Both passwords must match"
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

	});


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


	});

	// Remove username availability error message
	$("#mail").on("click", function(){
		$("#email_group p").html("");
	});

	// Alert on Resend page
	$("#resend-area button[type='submit']").on("click", function(){
		alert("We've sent another email. Please check your inbox.")
	});

});