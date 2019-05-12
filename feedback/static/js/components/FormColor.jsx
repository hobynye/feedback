import React, {Component} from 'react';
import Form from 'react-bootstrap/Form';
import ButtonGroup from 'react-bootstrap/ButtonGroup';

export default class FormColor extends Component {
    render() {
        return (
            <Form.Group controlId="formFeedbackColor" style={{"marginBottom": 0}}>
                <Form.Label>What kind of feedback is this?</Form.Label>
                <ButtonGroup data-toggle="buttons"
                             style={{"width": "100%", "display": "block"}}>
                    <label className="btn btn-success color-button active"
                           style={{"width": "33.33%"}} onClick={() => {this.props.handleColorChange("green")}} >
                        <Form.Check type="radio" name="color" id="green" autoComplete="off"
                                    label="Green" value="green" defaultChecked/>
                    </label>
                    <label className="btn btn-warning color-button"
                           style={{"width": "33.33%"}} onClick={() => {this.props.handleColorChange("yellow")}}>
                        <Form.Check type="radio" name="color" id="yellow" autoComplete="off"
                                    label="Yellow" value="yellow" />
                    </label>
                    <label className="btn btn-danger color-button"
                           style={{"width": "33.33%"}} onClick={() => {this.props.handleColorChange("red")}}>
                        <Form.Check type="radio" name="color" id="red" autoComplete="off"
                                    label="Red" value="red"/>
                    </label>
                </ButtonGroup>
            </Form.Group>
        )
    }
}