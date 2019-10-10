'use strict';

import {getArtistLink, getPlayButton, getSpotifyEmbedUriFromListen, getTrackLink} from './utils.jsx';

import APIService from './api-service';
import { AlertList } from 'react-bs-notifier';
import React from 'react';
import ReactDOM from 'react-dom';
import {SpotifyPlayer} from './spotify-player.jsx';
import {isEqual as _isEqual} from 'lodash';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEllipsisV } from '@fortawesome/free-solid-svg-icons'
import {CopyToClipboard} from 'react-copy-to-clipboard';

class MusicalOdyssey extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      alerts: [],
      listens: props.listens || [],
      currentListen : null,
      direction: "down",
      mode: props.mode || "similarity",
      mbid0: props.mbid0 || "",
      mbid1: props.mbid1 || "",
      metricsArray: props.metricsArray || [],
      limit: props.limit || 20
    };
    this.handleCurrentListenChange = this.handleCurrentListenChange.bind(this);
    this.handleSpotifyAccountError = this.handleSpotifyAccountError.bind(this);
    this.handleSpotifyPermissionError = this.handleSpotifyPermissionError.bind(this);
    this.isCurrentListen = this.isCurrentListen.bind(this);
    this.newAlert = this.newAlert.bind(this);
    this.onAlertDismissed = this.onAlertDismissed.bind(this);
    this.playListen = this.playListen.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
    this.getMetricsMultipleSelect = this.getMetricsMultipleSelect.bind(this);
    this.handleMetricSelectChange = this.handleMetricSelectChange.bind(this);
    this.handleOdysseyFormSubmit = this.handleOdysseyFormSubmit.bind(this);
    this.handleSimilarityFormSubmit = this.handleSimilarityFormSubmit.bind(this);
    this.getOdysseyForm = this.getOdysseyForm.bind(this);
    this.getSimilarityForm = this.getSimilarityForm.bind(this);
    this.navigateToSimilarTrack = this.navigateToSimilarTrack.bind(this);
    this.spotifyPlayer = React.createRef();

    this.APIService = new APIService(props.api_url || `${window.location.origin}/1`);
    if(this.state.mode === "odyssey" && this.state.mbid0 && this.state.mbid1){
      this.handleOdysseyFormSubmit();
    }
    else if(this.state.mode === "similarity" && this.state.mbid0) {
      this.handleSimilarityFormSubmit();
    }
  }

  handleSpotifyAccountError(error){
    this.newAlert("danger","Spotify account error", error);
    this.setState({canPlayMusic: false})
  }

  handleSpotifyPermissionError(error) {
    console.error(error);
    this.setState({canPlayMusic: false});
  }

  playListen(listen){
    if(this.spotifyPlayer.current){
      this.spotifyPlayer.current.playListen(listen);
      return;
    } else {
      // For fallback embedded player
      this.setState({currentListen:listen});
      return;
    }
  }

  handleCurrentListenChange(listen){
    this.setState({currentListen:listen});
  }
  isCurrentListen(listen){
    return this.state.currentListen && _isEqual(listen,this.state.currentListen);
  }

  newAlert(type, headline, message) {
    const newAlert ={
      id: (new Date()).getTime(),
      type,
      headline,
      message
    };

    this.setState({
      alerts: [...this.state.alerts, newAlert]
    });
  }
  onAlertDismissed(alert) {
    const alerts = this.state.alerts;

    // find the index of the alert that was dismissed
    const idx = alerts.indexOf(alert);

    if (idx >= 0) {
      this.setState({
        // remove the alert from the array
        alerts: [...alerts.slice(0, idx), ...alerts.slice(idx + 1)]
      });
    }
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.id;

    this.setState({
      [name]: value
    });
  }

  handleMetricSelectChange(event) {
    let selectedMetricsArray = [...event.target.selectedOptions]
      .filter(o => o.selected)
      .map(o => o.value);
    if (selectedMetricsArray.includes("all")) {
      selectedMetricsArray = ["all"];
    }
    this.setState({
      metricsArray: selectedMetricsArray
    })
  }
  getMetricsMultipleSelect() {
    return (<select
    multiple={true}
    className="form-control"
    id="metrics"
    value={this.state.metricsArray}
    onChange={this.handleMetricSelectChange} >
      <option key="all" value="all">Combine all metrics</option>
      {(this.props.metrics || []).map(metric =>
        <option key={metric} value={metric}>{metric}</option>
      )}
    </select>);
  }

  handleOdysseyFormSubmit(event) {
    console.debug(`Calling API with MBIDS ${this.state.mbid0} and ${this.state.mbid1}, metric ${this.state.metricsArray}`);
    event && event.preventDefault();
    this.APIService.getOdysseyPlaylist(this.state.mbid0,this.state.mbid1,this.state.metricsArray)
    .then(listens => this.setState({listens: listens || []}))
    .catch(error => this.newAlert("danger",`Error (${error.status})`, error.message))
  }
  
  handleSimilarityFormSubmit(event) {
    console.debug(`Calling  API to get tracks similar to MBID ${this.state.mbid0} according to metric ${this.state.metricsArray}, limited to ${this.state.limit} tracks`);
    event && event.preventDefault();
    this.APIService.getSimilarTracksPlaylist(this.state.mbid0,this.state.metricsArray,this.state.limit)
    //Do we need to order returned tracks by distance?
    .then(listens => this.setState({listens: _.sortBy(listens || [], 'track_metadata.additional_info.distance')}))
    .catch(error => this.newAlert("danger",`Error (${error.status})`, error.message))
  }
  
  getOdysseyForm() {
   return (
      <form onSubmit={this.handleOdysseyFormSubmit}>
        <p className="help-block">Enter two recording MBIDs to create a playlist</p>
        <table className="table table-border table-striped">
            <tbody>
            <tr>
                <td><label htmlFor="mbid0">Start track:</label></td>
                <td>
                    <input
                    className="form-control"
                    id="mbid0"
                    type="text"
                    value={this.state.mbid0}
                    onChange={this.handleInputChange} />
                </td>
            </tr>
            <tr>
                <td><label htmlFor="mbid1">End track:</label></td>
                <td>
                    <input
                    className="form-control"
                    id="mbid1"
                    type="text"
                    value={this.state.mbid1}
                    onChange={this.handleInputChange} />
                </td>
            </tr>
            <tr>
                <td><label htmlFor="metric">Metrics:</label></td>
                <td>
                    {this.getMetricsMultipleSelect()}
                </td>
            </tr>
            <tr>
                <td colSpan={2}>
                    <input className="btn btn-block btn-lg btn-primary" type="submit" value="Take me on a musical journey"/>
                </td>
            </tr>
          </tbody>
        </table>
    </form>)
  }
  
  getSimilarityForm() {
   return (
      <form onSubmit={this.handleSimilarityFormSubmit}>
        <p className="help-block">Enter a recording MBID to query for similar tracks according to a the selected metric</p>
        <table className="table table-border table-striped">
            <tbody>
            <tr>
                <td><label htmlFor="mbid0">Recording MBID:</label></td>
                <td>
                    <input
                    className="form-control"
                    id="mbid0"
                    type="text"
                    value={this.state.mbid0}
                    onChange={this.handleInputChange} />
                </td>
            </tr>
            <tr>
                <td><label htmlFor="metric">Metrics:</label></td>
                <td>
                  {this.getMetricsMultipleSelect()}
                </td>
            </tr>
            <tr>
                <td><label htmlFor="limit">Number of tracks:</label></td>
                <td>
                    <input
                    className="form-control"
                        id="limit"
                        type="number"
                        value={this.state.limit}
                        onChange={this.handleInputChange} />
                </td>
            </tr>
            <tr>
                <td colSpan={2}>
                    <input className="btn btn-block btn-lg btn-primary" type="submit" value={`Get me ${this.state.limit} similar tracks`}/>
                </td>
            </tr>
          </tbody>
        </table>
    </form>)
  }
  
  navigateToSimilarTrack(recordingMBID) {
    this.setState({mbid0: recordingMBID}, () => {
      switch (this.state.mode) {
        case "odyssey":
          this.handleOdysseyFormSubmit();
          break;
        case "similarity":
          this.handleSimilarityFormSubmit();
          break;
      }
    });
  }
  
  render() {

    const getSpotifyEmbedSrc = () => {
      if (this.state.currentListen)
      {
        return getSpotifyEmbedUriFromListen(this.state.currentListen);
      }
      return null;
    }
    let availableMetrics = this.state.listens.map(listen => {
      const metricsObject = _.get(listen,"track_metadata.additional_info.metrics");
      if(metricsObject){
        return Object.keys(metricsObject);
      }
    });
    availableMetrics =  _.uniq(_.flatten(availableMetrics));

    return (
      <div>
        <AlertList
          position="bottom-right"
          alerts={this.state.alerts}
          timeout={15000}
          dismissTitle="Dismiss"
          onDismiss={this.onAlertDismissed}
        />
        <div className="row">
          <div className="col-md-8">

            <h3>A musical odyssey</h3>
            <p>
              From {getTrackLink(this.state.listens.find(listen =>
                _.get(listen,"track_metadata.additional_info.recording_mbid") === this.state.mbid0))
                  || this.state.mbid0 }
              <br/>
              {this.state.mode === "odyssey" &&
                `to ${getTrackLink(this.state.listens.find(listen =>
                  _.get(listen,"track_metadata.additional_info.recording_mbid") === this.state.mbid1))
                  || this.state.mbid1}`
              }
            </p>
            {this.state.listens.length > 0 &&
              <div>
                <table className="table table-condensed table-striped listens-table" id="listens">
                  <thead>
                    <tr>
                      <th>Track</th>
                      <th>Artist</th>
                      {availableMetrics.map(metricName =>{
                        return <th>{metricName}</th>
                      })}
                      <th width="50px"></th>
                      <th width="50px"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {this.state.listens
                      .map((listen, index) => {
                        const recordingMBID = _.get(listen,"track_metadata.additional_info.recording_mbid");
                        return (
                          <tr key={index}
                            onDoubleClick={this.playListen.bind(this, listen)}
                            className={`listen ${this.isCurrentListen(listen) ? 'info' : ''}`}  >
                            <td>{getTrackLink(listen)}</td>
                            <td>{getArtistLink(listen)}</td>
                            {availableMetrics.map(metricName =>{
                              const value = _.get(listen,`track_metadata.additional_info.metrics.${metricName}`,"—");
                              return <th>{_.isNumber(value) ? _.round(value,6) : value}</th>
                            })}
                            <td>
                              <div className="btn-group">
                                <button disabled={!recordingMBID} type="button" className="btn btn-link dropdown-toggle"
                                data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                  <FontAwesomeIcon icon={faEllipsisV}/>
                                </button>
                                <ul className="dropdown-menu">
                                  <li>
                                    <CopyToClipboard text={recordingMBID}>
                                      <a>Copy recording MBID</a>
                                    </CopyToClipboard>
                                  </li>
                                  <li>
                                    <a href={`https://musicbrainz.org/recording/${recordingMBID}`}
                                      target="_blank">
                                      Open in MusicBrainz</a>
                                  </li>
                                  <li role="separator" className="divider"></li>
                                  <li>
                                    <a
                                      onClick={this.navigateToSimilarTrack.bind(this, recordingMBID)}>
                                        Explore from this track
                                    </a>
                                  </li>
                                </ul>
                              </div>
                            </td>
                            <td className="playButton">{getPlayButton(listen, this.playListen.bind(this, listen))}</td>
                          </tr>
                        )
                      })
                    }
                  </tbody>
                </table>
              </div>
            }
            <div className="tabbable">
              <ul className="nav nav-tabs">
                <li className={this.state.mode === "similarity"? "active" : ""}>
                  <a href="#similarityForm"
                  aria-controls="home" role="tab"
                  data-toggle="tab">Track similarity</a>
                </li>
                <li className={this.state.mode === "odyssey"? "active" : ""}>
                  <a href="#odysseyForm"
                  aria-controls="home" role="tab"
                  data-toggle="tab">Odyssey</a>
                </li>
              </ul>
              <div className="tab-content">
                <div role="tabpanel" className={`tab-pane ${this.state.mode === "similarity" ? "active" : ""}`}
                  id="similarityForm">
                  {this.getSimilarityForm()}
                </div>
                <div role="tabpanel" className={`tab-pane ${this.state.mode === "odyssey" ? "active" : ""}`}
                  id="odysseyForm">
                  {this.getOdysseyForm()}
                </div>
              </div>
            </div>
            <br/>
          </div>
          <div className="col-md-4" style={{ position: "-webkit-sticky", position: "sticky", top: 20 }}>
            {this.props.spotify.access_token && this.state.canPlayMusic !== false ?
              <SpotifyPlayer
                APIService={this.APIService}
                ref={this.spotifyPlayer}
                listens={this.state.listens}
                direction={this.state.direction}
                spotify_user={this.props.spotify}
                onCurrentListenChange={this.handleCurrentListenChange}
                onAccountError={this.handleSpotifyAccountError}
                onPermissionError={this.handleSpotifyPermissionError}
                currentListen={this.state.currentListen}
                newAlert={this.newAlert}
              /> :
              // Fallback embedded player
              <div className="col-md-4 text-right">
                <iframe src={getSpotifyEmbedSrc()}
                  width="300" height="380" frameBorder="0" allowtransparency="true" allow="encrypted-media">
                </iframe>
              </div>
            }
          </div>
        </div>
      </div>);
  }
}


let domContainer = document.querySelector('#react-container');
let propsElement = document.getElementById('react-props');
let reactProps;
try
{
  reactProps = JSON.parse(propsElement.innerHTML);
  // console.log("props",reactProps);
}
catch (err)
{
  console.error("Error parsing props:", err);
}
ReactDOM.render(<MusicalOdyssey {...reactProps}/>, domContainer);
