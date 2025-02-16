const ENV_HOME_PAGE = process.env.REACT_APP_HOME_PAGE === "true"; // Converts string to boolean

const config = {
  homePageEnabled: ENV_HOME_PAGE || false, // Default to false if undefined
};

export default config;

