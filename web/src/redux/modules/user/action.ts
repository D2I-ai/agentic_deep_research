import * as types from '../../mutation-types'

export const setToken = (token:string) => ({
    type: types.SET_TOKEN,
    token
});

export const login = (userData:any) => ({
    type: types.LOGIN,
    payload:userData,
});

export const logout = () => ({
    type: types.LOGOUT,
})