import React, {Component} from 'react';
import Container from 'react-bootstrap/Container';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button'
import UserDropdown from './UserDropdown';
import FormColor from './FormColor';
import FormBody from './FormBody';
import Modal from 'react-bootstrap/Modal'

export default class FeedbackForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            volunteer_id: "0",
            color: "green",
            body: "",
            modalShow: false,
            postSuccess: false,
            error: ""
        };
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleColorChange = this.handleColorChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        this.setState({
            [name]: value
        });
    }

    handleColorChange(color) {
        this.setState({color: color})
    }

    handleSubmit(event) {
        fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                author: this.state.volunteer_id,
                color: this.state.color,
                body: this.state.body
            })
        })
            .then((response) => response.json())
            .then((response) => {
                if (response.success) {
                    this.setState({postSuccess: true});
                } else {
                    this.setState({
                        postSuccess: false,
                        error: response.error
                    })
                }
            }).then(() => this.setState({modalShow: true}));

        event.preventDefault();
    };

    render() {
        let modalMessage;
        if (this.state.postSuccess) {
            modalMessage = (
                <div>
                    <h4>Thank you!</h4>
                    <p>Your feedback has been successfully submitted!</p>
                </div>
            )
        } else {
            modalMessage = (
                <div>
                    <h4>Uh oh... an error!</h4>
                    <p>Something happened that definitely shouldn't of: {this.state.error}</p>
                </div>
            )
        }
        return (
            <div>
                <Form onSubmit={this.handleSubmit}>
                    <Container className={"mt-3"}>
                        <Row>
                            <Col xl>
                                <Card style={{width: '100%'}}>
                                    <Card.Body>
                                        <Form.Group controlId="formVolunteerName" style={{"marginBottom": 0}}>
                                            <Form.Label>Lets start with your name!</Form.Label>
                                            <UserDropdown handleInputChange={this.handleInputChange} adminOnly={false}/>
                                            <Form.Text className="text-muted">
                                                Start by typing your name and selecting it from the dropdown.
                                            </Form.Text>
                                        </Form.Group>
                                    </Card.Body>
                                </Card>
                                <Card style={{width: '100%'}} className="mt-4">
                                    <Card.Body>
                                        <FormColor handleColorChange={this.handleColorChange}/>
                                    </Card.Body>
                                </Card>
                                <Card style={{width: '100%'}} className="mt-4">
                                    <Card.Body>
                                        <FormBody handleInputChange={this.handleInputChange}/>
                                    </Card.Body>
                                </Card>
                                <Button variant="primary" type="submit" className="mt-4" style={{width: '100%'}}>
                                    Submit Feedback
                                </Button>
                            </Col>
                        </Row>
                    </Container>
                </Form>
                <Modal
                    size="lg"
                    show={this.state.modalShow}
                    aria-labelledby="contained-modal-title-vcenter"
                    centered
                >
                    <Modal.Body>
                        {modalMessage}
                    </Modal.Body>
                    <Modal.Footer>
                        <Button onClick={() => location.reload()}>Close</Button>
                    </Modal.Footer>
                </Modal>
            </div>
        )
    }
}