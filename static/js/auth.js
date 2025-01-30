document.addEventListener("DOMContentLoaded", function () {
  // Initialize form handling for login and registration forms
  setupForm(
    "loginForm", // ID of the login form
    "loginButton", // ID of the login button
    "buttonText", // ID of the button text element
    "buttonSpinner", // ID of the loading spinner element
    loginUrl, // URL to send the login request
    dashboardUrl // Redirect URL on successful login
  );

  setupForm(
    "registerForm", // ID of the registration form
    "registerButton", // ID of the registration button
    "buttonText", // ID of the button text element
    "buttonSpinner", // ID of the loading spinner element
    registerUrl, // URL to send the registration request
    loginUrl // Redirect URL on successful registration (redirects to login)
  );
});

/**
 * Function to initialize form handling for login/registration.
 *
 * @param {string} formId - ID of the form to initialize.
 * @param {string} buttonId - ID of the submit button.
 * @param {string} textId - ID of the button's text element.
 * @param {string} spinnerId - ID of the button's spinner element.
 * @param {string} apiUrl - API endpoint URL for form submission.
 * @param {string} successRedirect - URL to redirect upon successful form submission.
 */
function setupForm(
  formId,
  buttonId,
  textId,
  spinnerId,
  apiUrl,
  successRedirect
) {
  let form = document.getElementById(formId);
  if (!form) return; // Exit if the form is not found

  form.addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent default form submission behavior

    // Get references to the button, text, and spinner elements
    let button = document.getElementById(buttonId);
    let buttonText = document.getElementById(textId);
    let buttonSpinner = document.getElementById(spinnerId);

    // Reset error messages before submission
    resetErrors(form);

    // Start loading state by disabling button and showing spinner
    toggleLoadingState(button, buttonText, buttonSpinner, true);

    // Collect form data and append CSRF token
    let formData = new FormData(form);
    formData.append(
      "csrf_token",
      document.querySelector("input[name='csrf_token']").value // Include CSRF token for security
    );

    try {
      // Send a POST request to the API with form data
      let response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      let result = await response.json();

      // Handle the response based on the success status
      if (result.success) {
        window.location.href = successRedirect; // Redirect on success
      } else {
        handleErrors(result.errors, form); // Display errors if any
      }
    } catch (error) {
      console.error("Error during form submission:", error); // Log any errors
    } finally {
      // Reset loading state
      toggleLoadingState(button, buttonText, buttonSpinner, false);
    }
  });

  // Listen for changes to input fields and remove error styles
  let fields = form.querySelectorAll("input");
  fields.forEach((field) => {
    field.addEventListener("input", function () {
      removeErrorStyles(field); // Remove error styles as user types
    });
  });
}

/**
 * Reset all error messages and styles on the form.
 *
 * @param {HTMLFormElement} form - The form element to reset errors for.
 */
function resetErrors(form) {
  // Clear error messages
  let errorElements = form.querySelectorAll(".error-message");
  errorElements.forEach((errorElement) => {
    errorElement.textContent = "";
    errorElement.classList.add("hidden"); // Hide error message
  });

  // Remove error styles from all input fields
  let fields = form.querySelectorAll("input");
  fields.forEach((field) => removeErrorStyles(field));
}

/**
 * Toggle the loading state of the submit button and spinner.
 *
 * @param {HTMLElement} button - The submit button element.
 * @param {HTMLElement} buttonText - The text element of the button.
 * @param {HTMLElement} buttonSpinner - The spinner element of the button.
 * @param {boolean} isLoading - Indicates whether the button is in loading state.
 */
function toggleLoadingState(button, buttonText, buttonSpinner, isLoading) {
  button.disabled = isLoading; // Disable button during loading
  buttonText.classList.toggle("hidden", isLoading); // Hide button text when loading
  buttonSpinner.classList.toggle("hidden", !isLoading); // Show spinner when loading
}

/**
 * Handle and display error messages for invalid form fields.
 *
 * @param {Object} errors - The errors object containing field error messages.
 * @param {HTMLFormElement} form - The form element to show errors on.
 */
function handleErrors(errors, form) {
  // Iterate over each error and display it
  for (let fieldId in errors) {
    showError(form, fieldId, errors[fieldId]); // Show specific error message for each field
  }
}

/**
 * Show an error message next to the relevant form field.
 *
 * @param {HTMLFormElement} form - The form element containing the field.
 * @param {string} fieldId - The ID of the form field with the error.
 * @param {string} message - The error message to display.
 */
function showError(form, fieldId, message) {
  let field = form.querySelector(`#${fieldId}`);
  let errorElement = form.querySelector(`#${fieldId}Error`);

  if (errorElement) {
    errorElement.textContent = message; // Display error message
    errorElement.classList.remove("hidden"); // Make error message visible
  }

  if (field) {
    field.classList.add("border-red-500", "focus:ring-red-400"); // Add error styles to the field
  }
}

/**
 * Remove error styles from a field when the user starts typing.
 *
 * @param {HTMLInputElement} field - The input field to remove error styles from.
 */
function removeErrorStyles(field) {
  field.classList.remove("border-red-500", "focus:ring-red-400"); // Remove error border and focus styles
  let errorElement = document.getElementById(`${field.id}Error`);
  if (errorElement) errorElement.classList.add("hidden"); // Hide the error message
}








document.addEventListener("DOMContentLoaded", () => {
    const menuToggle = document.getElementById("menuToggle");
    const mobileMenu = document.getElementById("mobileMenu");
    const lines = document.querySelectorAll(".hamburger-line");
  
    let menuOpen = false;
  
    menuToggle.addEventListener("click", () => {
      menuOpen = !menuOpen;
  
      // Animate the menu dropdown
      if (menuOpen) {
        mobileMenu.classList.remove("scale-y-0");
        mobileMenu.classList.add("scale-y-100");
      } else {
        mobileMenu.classList.remove("scale-y-100");
        mobileMenu.classList.add("scale-y-0");
      }
  
      // Animate the hamburger icon to an "X"
      lines[0].classList.toggle("rotate-45", menuOpen);
      lines[0].classList.toggle("translate-y-2", menuOpen);
      lines[1].classList.toggle("opacity-0", menuOpen);
      lines[2].classList.toggle("-rotate-45", menuOpen);
      lines[2].classList.toggle("-translate-y-2", menuOpen);
    });
  });
  
