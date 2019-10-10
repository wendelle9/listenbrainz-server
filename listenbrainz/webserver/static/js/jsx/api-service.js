import {isFinite, isNil, isString} from 'lodash';

export default class APIService {
  
  APIBaseURI;

  constructor(APIBaseURI){
    if(isNil(APIBaseURI) || !isString(APIBaseURI)){
      throw new SyntaxError(`Expected API base URI string, got ${typeof APIBaseURI} instead`)
    }
    if(APIBaseURI.endsWith('/')){
      APIBaseURI = APIBaseURI.substring(0, APIBaseURI.length-1);
    }
    if(!APIBaseURI.endsWith('/1')){
      APIBaseURI += '/1';
    }
    this.APIBaseURI = APIBaseURI;
  }

  async getRecentListensForUsers(userNames, limit) {
    let userNamesForQuery = userNames;
    if (Array.isArray(userNames)){
      userNamesForQuery = userNames.join(',');
    }
    else if(typeof userNames !== 'string') {
      throw new SyntaxError(`Expected username or array of username strings, got ${typeof userNames} instead`);
    }

    let query = `${this.APIBaseURI}/users/${userNamesForQuery}/recent-listens`;

    if(!isNil(limit) && isFinite(Number(limit))){
      query += `?limit=${limit}`
    }
    
    const response = await fetch(query, {
      accept: 'application/json',
      method: "GET"
    })
    await this.checkStatus(response);
    const result = await response.json();
    
    return result.payload.listens
  }
  
  async getListensForUser(userName, minTs, maxTs, count) {
    
    if(typeof userName !== 'string'){
      throw new SyntaxError(`Expected username string, got ${typeof userName} instead`);
    }
    if(!isNil(maxTs) && !isNil(minTs)) {
      throw new SyntaxError('Cannot have both minTs and maxTs defined at the same time');
    }

    let query = `${this.APIBaseURI}/user/${userName}/listens`;

    const queryParams = [];
    if(!isNil(maxTs) && isFinite(Number(maxTs))){
      queryParams.push(`max_ts=${maxTs}`)
    }
    if(!isNil(minTs) && isFinite(Number(minTs))){
      queryParams.push(`min_ts=${minTs}`)
    }
    if(!isNil(count) && isFinite(Number(count))){
      queryParams.push(`count=${count}`)
    }
    if(queryParams.length) {
      query += `?${queryParams.join("&")}`
    }

    const response = await fetch(query, {
      accept: 'application/json',
      method: "GET"
    })
    await this.checkStatus(response);
    const result = await response.json();
    
    return result.payload.listens
  }

  async refreshSpotifyToken(){
    const response = await fetch("/profile/refresh-spotify-token",{method:"POST"})
    await this.checkStatus(response);
    const result = await response.json();
    return result.user_token;
  }
  
  async getOdysseyPlaylist(startTrack, endTrack, metricsArray) {
    
    if(isNil(startTrack) || isNil(endTrack) || startTrack === "" || endTrack === "") {
      throw new SyntaxError('Expected a startTrack and an endTrack');
    }

    let query = `${this.APIBaseURI}/odyssey/${startTrack}/${endTrack}`;

    if(!isNil(metricsArray)){
      query += `?metrics=${metricsArray}`
    }

    const response = await fetch(query, {
      accept: 'application/json',
      method: "GET"
    })
    await this.checkStatus(response);
    const result = await response.json();
    
    return result.payload
  }

  async getSimilarTracksPlaylist(recordingMBID, metricsArray, limit) {
    if(isNil(recordingMBID) || recordingMBID === "") {
      throw new SyntaxError('Expected a recordingMBID');
    }

    let query = `${this.APIBaseURI}/odyssey/similar/${recordingMBID}`;

    const queryParams = [];
    if(!isNil(metricsArray)){
      queryParams.push(`metrics=${metricsArray}`)
    }
    if(!isNil(limit) && isFinite(Number(limit))){
      queryParams.push(`limit=${limit}`)
    }
    if(queryParams.length) {
      query += `?${queryParams.join("&")}`
    }
    const response = await fetch(query, {
      accept: 'application/json',
      method: "GET"
    })
    await this.checkStatus(response);
    const result = await response.json();
    
    return result.payload
  }
  
  async checkStatus(response) {
    if (response.ok || (response.status >= 200 && response.status < 300)) {
      return;
    }
    let errorMessage = `HTTP Error ${response.statusText}`
    try {
      // The API will return an JSON error object with properties {code, error}
      const errorObject = await response.json();
      errorMessage = errorObject.error
    } catch (err) {
    }
    const error = new Error(errorMessage);
    error.status = response.status;
    error.response = response;
    throw error;
  }
}