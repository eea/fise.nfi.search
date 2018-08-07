import axios from 'axios';

const logRequests = process.env.NODE_ENV === 'development';


const _backend_host = process.env.BACKEND_HOST;
const _backend_port = process.env.BACKEND_PORT && Number(process.env.BACKEND_PORT) ? `:${process.env.BACKEND_PORT}` : '';
const _script_name = process.env.SCRIPT_NAME || '';

const _protocol = location.protocol;

const apiURL = `${_protocol}//${_backend_host}${_backend_port}${_script_name}/api/`;

const api = axios.create({
  baseURL: apiURL,
  withCredentials: true,
});

api.defaults.xsrfHeaderName = "X-CSRFTOKEN";
api.defaults.xsrfCookieName = "csrftoken";

function fetchFacets(path) {
  // logRequests && console.log(`fetching ${path}...`);
  return api.get('facets/' + path);
}

function fetchSearch(path) {
  // logRequests && console.log(`fetching ${path}...`);
  return api.get('search/' + path);
}

function fetch(path) {
  // logRequests && console.log(`fetching ${path}...`);
  return api.get(path);
}

function post(path, data) {
  // logRequests && console.log(`posting ${path} with data ${data}...`);
  return api.post(path, data);
}

function update(path, data) {
  // logRequests && console.log(`patching ${path} with data ${data}...`);
  return api.patch(path, data);
}

function remove(path) {
  // logRequests && console.log(`removig ${path} ...`);
  return api.delete(path);
}

function searchFullUrl(path) {
  // logRequests && console.log(`fetching ${path} ...`);
  return axios.get(path);
}

export { fetch, fetchFacets, fetchSearch, searchFullUrl, post, update, remove };
