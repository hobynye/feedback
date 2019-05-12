import React, {Component} from 'react';
import Form from 'react-bootstrap/Form'

export default class FormBody extends Component {
    render() {
        return (
            <Form.Group controlId="formFeedbackBody">
                <Form.Label>Okay, whats your message?</Form.Label>
                <Form.Control name="body" as="textarea" rows="3" onChange={this.props.handleInputChange}/>
            </Form.Group>
        )
    }
}