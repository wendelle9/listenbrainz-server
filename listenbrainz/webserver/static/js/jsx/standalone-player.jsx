'use strict';

import {getArtistLink, getPlayButton, getSpotifyEmbedUriFromListen, getTrackLink} from './utils.jsx';
import APIService from './api-service';
import React from 'react';
import ReactDOM from 'react-dom';
import { AlertList } from 'react-bs-notifier';
import {SpotifyPlayer} from './spotify-player.jsx';

import { faList, faHeadphones } from '@fortawesome/free-solid-svg-icons'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

class StandalonePlayer extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      alerts: [],
      listens: props.recordings || [],
      currentListen : null,
      playlistMetadata: props.metadata,
      showBack: props.recordings.length ? false : true
    };
    this.handleCurrentListenChange = this.handleCurrentListenChange.bind(this);
    this.handleSpotifyAccountError = this.handleSpotifyAccountError.bind(this);
    this.handleSpotifyPermissionError = this.handleSpotifyPermissionError.bind(this);
    this.newAlert = this.newAlert.bind(this);
    this.onAlertDismissed = this.onAlertDismissed.bind(this);
    this.playListen = this.playListen.bind(this);
    this.onFlipButtonClick = this.onFlipButtonClick.bind(this);
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

  onFlipButtonClick() {
    this.setState({showBack: !this.state.showBack});
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
  
  render() {

    const getSpotifyEmbedSrc = () => {
      if (this.state.currentListen)
      {
        return getSpotifyEmbedUriFromListen(this.state.currentListen);
      }
      return null;
    }
    const name = (!!this.state.playlistMetadata && this.state.playlistMetadata.name) || "Playlist";
    const created_at = !!this.state.playlistMetadata && this.state.playlistMetadata.created;
    const description = !!this.state.playlistMetadata && this.state.playlistMetadata.description;

    return (
      <div>
        <AlertList
          position="bottom-right"
          alerts={this.state.alerts}
          timeout={15000}
          dismissTitle="Dismiss"
          onDismiss={this.onAlertDismissed}
        />
        <div id="standalone-player" className={`${this.state.showBack ? 'flip':''}`}>
          <button className="btn btn-xs flip-button" onClick={this.onFlipButtonClick}>
            <FontAwesomeIcon icon={this.state.showBack ? faHeadphones : faList}></FontAwesomeIcon>
          </button>
          <div className="flipper">
            <div className="front">
              {this.props.spotify.access_token && this.state.canPlayMusic !== false ?
                <SpotifyPlayer
                  APIService={this.APIService}
                  ref={this.spotifyPlayer}
                  listens={this.state.listens}
                  spotify_user={this.props.spotify}
                  onCurrentListenChange={this.handleCurrentListenChange}
                  onAccountError={this.handleSpotifyAccountError}
                  onPermissionError={this.handleSpotifyPermissionError}
                  currentListen={this.state.currentListen}
                  newAlert={this.newAlert}
                  direction="hidden"
                /> :
                // Fallback embedded player
                <iframe src={getSpotifyEmbedSrc()}
                  width="300" height="380" frameBorder="0" allowtransparency="true" allow="encrypted-media">
                </iframe>
              }
            </div>
            <div className="back">
              <div className="scroll-hint"></div>
              {this.state.playlistMetadata &&
                <div className="header">
                  <h4 title={name}>{name}
                  {created_at && <small className="pull-right">— {new Date(created_at).toLocaleString()}</small>}
                  </h4>
                  {description && <small title={description}>{description}</small>}
                </div>
              }
              {this.state.listens.length > 0 ?
                <div id="listens">
                  <table className="table table-condensed table-striped listens-table">
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
                            <tr key={`listen_${index}`}
                              onDoubleClick={this.playListen.bind(this, listen)} >
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
              :
                <div className="lead text-center">
                  <p>Nothing to play</p>
                </div>
              }
            </div>
          </div>
        </div>
      </div>
    );
  }
}


let domContainer = document.querySelector('#react-container');
let propsElement = document.getElementById('react-props');
let reactProps;
try
{
  reactProps = JSON.parse(propsElement.innerHTML);
}
catch (err)
{
  console.error("Error parsing props:", err);
}
ReactDOM.render(<StandalonePlayer {...reactProps}/>, domContainer);
