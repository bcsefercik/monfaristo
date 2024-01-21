import axios from "axios";

import { getServerSession } from "next-auth";
import { getSession } from "next-auth/react";
import { API_HOST } from "../constants";
const rootURL = API_HOST;
const baseURL = rootURL;

export const defaultErrorMessage = "Unexpected error occurred";
export const TIMEOUT = 20000;
export const MAX_TIMEOUT = 60000;
export const ADDITIONAL_CONTEXT_REQUESTED_COOKIE =
  "X-Monfaristo-Additional-Context-Requested";

export const apiHeaders = {
  "X-Requested-With": "XMLHttpRequest",
  ...createAdditionalContextHeader(),
};

const mApi = createAPI({ baseURL });
mApi.defaults.headers.common["Content-Type"] = "application/json";
mApi.get = withTrailingSlashCheck(mApi.get);
mApi.post = withTrailingSlashCheck(mApi.post);
mApi.put = withTrailingSlashCheck(mApi.put);
mApi.patch = withTrailingSlashCheck(mApi.patch);
export default mApi;
export function createAPI(params: any) {
  const api = axios.create({
    headers: apiHeaders,
    timeout: MAX_TIMEOUT,
    ...params,
  });

  api.interceptors.request.use(async (request) => {
    if (request.headers.Authorization) return request;
    let session;

    if (typeof window !== "undefined") {
      session = await getSession();
    } else {
      session = await getServerSession();
    }

    if (session) {
      const authHeaderValue = `Bearer ${(session as any).apiToken}`;

      request.headers.Authorization = authHeaderValue;
      api.defaults.headers.common.Authorization = authHeaderValue;
    }

    return request;
  });

  // api.interceptors.response.use(
  //   (response) => response,
  //   async (error: AxiosError) => {

  //     api.defaults.headers.common.Authorization = undefined
  //     await signOut({ callbackUrl: '/' })

  //     return Promise.reject(error)
  //   },
  // )

  return api;
}

function withTrailingSlashCheck(req) {
  return function (url, ...rest) {
    const errorMessage = `Deprecated API call without trailing slash detected: "${url}". Fix this by adding trailing slash`;
    const parsedUrl = new URL(url, "https://example.com");
    if (parsedUrl.pathname.endsWith("/")) {
      throw Error(errorMessage);
    }
    if (parsedUrl.pathname.includes("//")) {
      throw Error(
        `Double slashes detected in: ${url}. Might be a hint that the url is wrong`
      );
    }
    return req(url, ...rest);
  };
}

function createAdditionalContextHeader() {
  return {};
  // try {
  //   const cookieStore = cookies();
  //   const cookie = cookieStore.get(ADDITIONAL_CONTEXT_REQUESTED_COOKIE);
  //   const contextRequested = cookie && JSON.parse(cookie.value);
  //   return contextRequested && !contextRequested.requires_api_call
  //     ? {
  //         ADDITIONAL_CONTEXT_REQUESTED_COOKIE: JSON.stringify(
  //           contextRequested.value
  //         ),
  //       }
  //     : {};
  // } catch (error) {
  //   return {};
  // }
}
