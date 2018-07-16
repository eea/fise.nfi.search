'use strict'
module.exports = {
  NODE_ENV: '"production"',
  BACKEND_HOST: JSON.stringify(process.env.BACKEND_HOST),
  BACKEND_PORT: JSON.stringify(process.env.BACKEND_PORT),
  SCRIPT_NAME: JSON.stringify(process.env.SCRIPT_NAME),
}
