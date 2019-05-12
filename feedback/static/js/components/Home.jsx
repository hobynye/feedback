import React, {Component} from 'react';
import Navigation from './Navigation';
import FeedbackForm from './FeedbackForm';


export default class Home extends Component {
    render() {
        return (
            <div>
                <Navigation/>
                <FeedbackForm/>
            </div>
        )
    }
}
