import { createStore } from 'vuex'
import auth from './modules/auth'
import users from './modules/users'
import ipPools from './modules/ipPools'
import ipAllocations from './modules/ipAllocations'
import vps from './modules/vps'
import app from './modules/app'

export default createStore({
  modules: {
    auth,
    users,
    ipPools,
    ipAllocations,
    vps,
    app
  }
}) 