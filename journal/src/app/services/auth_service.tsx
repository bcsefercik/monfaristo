import axios from "axios";
import { API_HOST } from "../constants";

export const authenticate =  async (email: string, password: string): any => {
  var userInfo = undefined;

  var bodyFormData = new FormData();
  bodyFormData.append("username", email);
  bodyFormData.append("password", password);

  await axios.
    post(`${API_HOST}/user/token`, bodyFormData, {
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
      } as any;
    })
    .catch((error) => {
      return undefined;
    });

  return userInfo;
};
