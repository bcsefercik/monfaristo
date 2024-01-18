import mApi from "../utils/m-api";

export const authenticate =  async (email: string, password: string): any => {
  var userInfo = undefined;

  var bodyFormData = new FormData();
  bodyFormData.append("username", email);
  bodyFormData.append("password", password);

  await mApi
    .post("/user/token", bodyFormData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => {
      userInfo = {
        token: response.data.access_token,
        user: {
          email,
          password,
        },
      };
    })
    .catch((error) => {
      return undefined;
    });

  return userInfo;
};
