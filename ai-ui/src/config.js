// Get query parameters from the current URL
const queryParams = new URLSearchParams(window.location.search);
const homeParam = queryParams.get("home"); // Get the 'home' query parameter

// Convert to a boolean if it's set in the URL, otherwise check the env variable
const ENV_HOME_PAGE = process.env.REACT_APP_HOME_PAGE === "true"; // Convert env to boolean
const HOME_PAGE_ENABLED = homeParam !== null ? homeParam === "true" : ENV_HOME_PAGE; // Override logic

const config = {
  homePageEnabled: HOME_PAGE_ENABLED, // Final decision on home page visibility
};

export default config;

