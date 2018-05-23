import axios from 'axios';

const logRequests = process.env.NODE_ENV === 'development';

const BACKEND_HOST = 'localhost';
const BACKEND_PORT = 8000;
const _backend_host = process.env.BACKEND_HOST || BACKEND_HOST;
const _backend_port = process.env.BACKEND_PORT && Number(process.env.BACKEND_PORT) || BACKEND_PORT;

const apiURL = `http://${_backend_host}:${_backend_port}/api/0.1/`;

const api = axios.create({
  baseURL: apiURL,
  withCredentials: true,
});


api.defaults.xsrfHeaderName = "X-CSRFTOKEN";
api.defaults.xsrfCookieName = "csrftoken";

function fetch(path) {
  logRequests && console.log(`fetching ${path}...`);
  return api.get(path);
}

function post(path, data) {
  logRequests && console.log(`posting ${path} with data ${data}...`);
  return api.post(path, data);
}

function update(path, data) {
  logRequests && console.log(`patching ${path} with data ${data}...`);
  return api.patch(path, data);
}

function remove(path) {
  logRequests && console.log(`removig ${path} ...`);
  return api.delete(path);
}

export { apiURL, api, fetch, post, update, remove };
