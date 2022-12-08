import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  CognitoUserAttribute
} from 'amazon-cognito-identity-js'
//import { Config, CognitoIdentityCredentials } from 'aws-sdk'
import * as AWS from 'aws-sdk';
import store from '@/store'

export default class Cognito {
  //private userPool
  //private options
  //private currentUser
  //private poolData
  //public cognitoCreds

  constructor() {
    this.userPool = null
    this.options= null
  }

  configure(config) {
    if (config.userPool) {
      this.userPool = config.userPool
    } else {
      this.userPool = new CognitoUserPool({
        UserPoolId: config.UserPoolId,
        ClientId: config.ClientId
      })
    }
    AWS.config.region = config.region
    AWS.config.credentials = new AWS.CognitoIdentityCredentials({
      IdentityPoolId: config.IdentityPoolId
    })
    this.options = config
    this.currentUser = false
  }

  static install(Vue, options) {
    Object.defineProperty(Vue.prototype, '$cognito', {
      get () { return this.$root._cognito }
    })

    Vue.mixin({
      beforeCreate () {
        if (this.$options.cognito) {
          this._cognito = this.$options.cognito
          this._cognito.configure(options)
        }
      }
    })
  }

  signUp(username, password) {
    const name = { Name: 'name', Value: username }
    const email = { Name: 'email', Value: username }
    const now = Math.floor(new Date().getTime() / 1000)
    const updatedAt = { Name: 'updated_at', Value: String(now) }

    const attributeList = []
    attributeList.push(new CognitoUserAttribute(name))
    attributeList.push(new CognitoUserAttribute(email))
    attributeList.push(new CognitoUserAttribute(updatedAt))

    return new Promise((resolve, reject) => {
    if (this.userPool == null) return
      this.userPool.signUp(username, password, attributeList, [], (err, result) => {
        if (err) {
          reject(err)
        } else {
          resolve(result)
        }
      })
    })
  }

  // code confirmation on sign up
  confirmation(username, confirmationCode) {
    if (this.userPool == null) return
    const userData = { Username: username, Pool: this.userPool }
    const cognitoUser = new CognitoUser(userData)
    return new Promise((resolve, reject) => {
      cognitoUser.confirmRegistration(confirmationCode, true, (err, result) => {
        if (err) {
          reject(err)
        } else {
          resolve(result)
        }
      })
    })
  }

  signIn(username, password) {
    if (this.userPool == null) return

    const userData = { Username: username, Pool: this.userPool }
    const cognitoUser = new CognitoUser(userData)
    const authenticationData = { Username: username, Password: password }
    const authenticationDetails = new AuthenticationDetails(authenticationData)
    return new Promise((resolve, reject) => {
      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess(result) {
          resolve(result)
        },
        onFailure(err) {
          reject(err)
        },
        //newPasswordRequired(userAttributes, requiredAttributes) {
        //  cognitoUser.completeNewPasswordChallenge(password, {}, this);
        //},
      })
    })
  }

  signOut() {
    if (this.userPool == null) return
    const currentUser = this.userPool.getCurrentUser()
    if (currentUser) {
      currentUser.signOut()
    }
  }

  isAuthenticated() {
    return new Promise((resolve, reject) => {
      if (this.userPool == null) return
      this.currentUser = this.userPool.getCurrentUser()
      if (this.currentUser === null) { reject(this.currentUser) }
      this.currentUser.getSession((err, session) => {
        if (err) {
          reject(err)
        } else {
          if (!session.isValid()) {
            reject(session)
          } else {
            resolve(session)
          }
        }
      })
    })
  }

  getAttribute() {
    return new Promise((resolve, reject) => {
      this.currentUser.getUserAttributes((err, result) => {
        if (err) {
          reject(err)
        }
        else {
          resolve(result)
        }
      })
    })
  }

  resentCode() {
    return new Promise((resolve, reject) => {
      this.currentUser.getAttributeVerificationCode('email', {
        onSuccess: (result) => {
          console.log('success getAttributeVerificationCode')
          resolve(result)
        },
        onFailure: (err) => {
          console.log('failed getAttributeVerificationCode: ' + JSON.stringify(err))
          reject(err)
        }
      })
    })
  }

  // Enable email after email updated
  verifyAttribute(confirmationCode) {
    return new Promise((resolve, reject) => {
      this.currentUser.verifyAttribute('email', confirmationCode, {
        onSuccess: (result) => {
          console.log('email verification success')
          var user = store.getters.user
          user['email_verified'] = 'true'
          store.commit('setUser', user)
          resolve(result)
        },
        onFailure: (err) => {
          console.log('email verification failed')
          reject(err)
        }
      })
    })
  }

  updateEmailAddress(email) {
    let attributes = {
      'email': email,
      'name': email
    }
    return new Promise((resolve, reject) => {
      this.updateAttributes(attributes)
        .then(result => { // eslint-disable-line
          resolve(result)
          var user = store.getters.user
          user['email_verified'] = 'false'
          store.commit('setUser', user)
        })
        .catch(err => {
          reject(err)
        })
    })
  }

  updatePassword(oldPassword, newPassword) {
    return new Promise((resolve, reject) => {
      this.currentUser.changePassword(oldPassword, newPassword, (err, result) => {
        if (err) {
          reject(err)
        }
        else {
          resolve(result)
        }
      })
    })
  }

  // send mail for password reset
  forgetPassword(username) {
    if (this.userPool == null) return
    const userData = { Username: username, Pool: this.userPool }
    const cognitoUser = new CognitoUser(userData)
    return new Promise((resolve, reject) => {
      cognitoUser.forgotPassword({
        onSuccess: (result) => {
          console.log('email verification success')
          resolve(result)
        },
        onFailure: (err) => {
          console.log('email verification failed')
          reject(err)
        }
      })
    })
  }

  resetPassword(username, newPassword, code) {
    const userData = { Username: username, Pool: this.userPool }
    const cognitoUser = new CognitoUser(userData)
    return new Promise((resolve, reject) => {
      cognitoUser.confirmPassword(code, newPassword, {
        onSuccess: (result) => {
          console.log('password reset success')
          resolve(result)
        },
        onFailure: (err) => {
          console.log('password reset failed')
          reject(err)
        }
      })
    })
  }

  // Update profile
  updateAttributes(attributes) {
    const attributeList = []
    for(var key in attributes) {
      const attribute = { Name: key, Value: attributes[key] }
      attributeList.push(new CognitoUserAttribute(attribute))
    }
    return new Promise((resolve, reject) => {
      if (this.currentUser === null) { reject(this.currentUser) }

      // update attributes
      this.currentUser.updateAttributes(attributeList, (err, result) => {
        if (err) {
          reject(err)
        } else {
          var user = store.getters.user
          for(var key in attributes) {
            user[key] = attributes[key]
          }
          store.commit('setUser', user)
          resolve(result)
        }
      })
    })
  }
}
