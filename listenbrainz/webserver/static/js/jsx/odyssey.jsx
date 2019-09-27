'use strict';

import {getArtistLink, getPlayButton, getSpotifyEmbedUriFromListen, getTrackLink} from './utils.jsx';

import APIService from './api-service';
import { AlertList } from 'react-bs-notifier';
import React from 'react';
import ReactDOM from 'react-dom';
import {SpotifyPlayer} from './spotify-player.jsx';
import {isEqual as _isEqual} from 'lodash';

class MusicalOdyssey extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      alerts: [],
      listens: props.listens || [],
      currentListen : null,
      direction: "down",
      startTrack: "",
      endTrack: "",
      numberOfSteps: 25
    };
    this.handleCurrentListenChange = this.handleCurrentListenChange.bind(this);
    this.handleSpotifyAccountError = this.handleSpotifyAccountError.bind(this);
    this.handleSpotifyPermissionError = this.handleSpotifyPermissionError.bind(this);
    this.isCurrentListen = this.isCurrentListen.bind(this);
    this.newAlert = this.newAlert.bind(this);
    this.onAlertDismissed = this.onAlertDismissed.bind(this);
    this.playListen = this.playListen.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.spotifyPlayer = React.createRef();

    this.APIService = new APIService(props.api_url || `${window.location.origin}/1`);
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

  handleSubmit(event) {
    console.debug(`Calling API with MBIDS ${this.state.startTrack} and ${this.state.endTrack}, ${this.state.numberOfSteps} steps in-between`);
    event.preventDefault();
    this.APIService.getOdysseyPlaylist(this.state.startTrack,this.state.endTrack,this.state.numberOfSteps)
    .then(listens => this.setState({listens: listens || []}))
    .catch(error => this.newAlert("danger",`Error (${error.status})`, error.message))
  }
  
  
  render() {

    const getSpotifyEmbedSrc = () => {
      if (this.state.currentListen)
      {
        return getSpotifyEmbedUriFromListen(this.state.currentListen);
      }
      return null;
    }

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

            {!this.state.listens.length &&
            <form onSubmit={this.handleSubmit}>
                <p>Enter two tracks' MBID to create a playlist with X steps in-between</p>
                <table className="table table-border table-striped">
                    <tbody>
                    <tr>
                        <td><label for="startTrack">Start track:</label></td>
                        <td>
                            <input
                            className="form-control"
                            id="startTrack"
                            type="text"
                            value={this.state.startTrack}
                            onChange={this.handleInputChange} />
                        </td>
                    </tr>
                    <tr>
                        <td><label for="endTrack">End track:</label></td>
                        <td>
                            <input
                            className="form-control"
                            id="endTrack"
                            type="text"
                            value={this.state.endTrack}
                            onChange={this.handleInputChange} />
                        </td>
                    </tr>
                    <tr>
                        <td><label for="numberOfSteps">Number of tracks:</label></td>
                        <td>
                            <input
                            className="form-control"
                                id="numberOfSteps"
                                type="number"
                                value={this.state.numberOfSteps}
                                onChange={this.handleInputChange} />
                        </td>
                    </tr>
                    <tr>
                        <td colSpan={2}>
                            <input className="btn btn-block btn-lg btn-primary" type="submit" value="Take me on an odyssey"/>
                        </td>
                    </tr>
                  </tbody>
                </table>
            </form>
            }
            {this.state.listens.length > 0 &&
              <div>
                <table className="table table-condensed table-striped listens-table" id="listens">
                  <thead>
                    <tr>
                      <th>Track</th>
                      <th>Artist</th>
                      <th width="50px"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {this.state.listens
                      .map((listen, index) => {
                        return (
                          <tr key={index}
                            onDoubleClick={this.playListen.bind(this, listen)}
                            className={`listen ${this.isCurrentListen(listen) ? 'info' : ''}`}  >
                            <td>{getTrackLink(listen)}</td>
                            <td>{getArtistLink(listen)}</td>
                            <td className="playButton">{getPlayButton(listen, this.playListen.bind(this, listen))}</td>
                          </tr>
                        )
                      })
                    }
                  </tbody>
                </table>
              </div>
            }
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


