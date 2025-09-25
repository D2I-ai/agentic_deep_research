import * as types from '../../mutation-types'

export const setDbId = (dbId:string,dbName?:string) => ({
    type: types.SET_DBID,
    dbId,
    dbName
});

export const setDbTabs = (dbtabs:Array<any>) => ({
    type: types.SET_DBTABS,
    dbtabs,
});
