import React from 'react';
import moment from 'moment';
import styles from './styles.scss';

export default class Dashboard extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      speed: 0.0,
      distance: 0.0,
      pace: moment.duration(0),
      rpm: 0
    };
  }

  componentDidMount() {
    const ws = new WebSocket("ws://127.0.0.1:8765/ws");
    //const ws = new WebSocket("ws://localhost:8765/ws");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.telemetry != null) {
        this.setState({
          speed: data.telemetry.km_per_hr.toFixed(1),
          distance: data.telemetry.distance_travelled_km.toFixed(2),
          pace: moment.duration(data.telemetry.pace * 1000),
          rpm: data.telemetry.rpm.toFixed(0)
        });
      }
    };
  }

  render() {
    return (
      <div className={styles.dashboard}>
        <div className={styles.row}>
          <Stat title="Speed" unit="km/h" value={this.state.speed} />
          <Stat title="Distance" unit="km" value={this.state.distance} />
          <DurationStat title="Pace" value={this.state.pace} />
          <Stat title="RPM" unit="rpm" value={this.state.rpm} />
        </div>
      </div>
    );
  }
}

class Stat extends React.Component {
  render() {
    return (
      <figure className={styles.stat}>
        <figcaption className={styles.stat__title}>{this.props.title}</figcaption>
        <div className={styles.stat__value}>
          {this.formatValue(this.props.value)}
          <span className={styles.stat__unit}>{this.props.unit}</span>
        </div>
      </figure>
    );
  }

  formatValue(value) {
    return value.toString();
  }
}

class DurationStat extends Stat {
  formatValue(value) {
    if (value.asMinutes() < 1) {
      return value.seconds();
    }

    return value.minutes() + ':' + value.seconds();
  }
}

