import Vue from 'vue'
import Cognito from './cognito'
import cognitoConfig from '@/config/cognito-client-config'

Vue.use(Cognito, cognitoConfig)

export default new Cognito()
