import React, {Component} from 'react';
import Container from 'react-bootstrap/Container';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button'
import UserDropdown from './UserDropdown';
import Navigation from './Navigation';
import Alert from 'react-bootstrap/Alert';

function getUrlVars() {
    let vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function getUrlParam(parameter, defaultValue){
    let urlParameter = defaultValue;
    if(window.location.href.indexOf(parameter) > -1){
        urlParameter = getUrlVars()[parameter];
        }
    return urlParameter;
}

export default class Login extends Component {
    constructor(props) {
        super(props);
        this.state = {
            error: false,
            volunteer_id: "",
            password: ""
        };
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        console.log({name: name, value: value});
        this.setState({
            [name]: value
        });
    }

    handleSubmit(event) {
        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                volunteer_id: this.state.volunteer_id,
                password: this.state.password,
                next: getUrlParam("next", "/")
            })
        })
            .then((response) => response.json())
            .then((response) => {
                if (!response.success) {
                    this.setState({
                        error: true
                    })
                } else {
                    window.location.replace(response.next);
                }

            });
        event.preventDefault();
    };

    render() {
        let errorBanner;
        if (this.state.error) {
            errorBanner = (
                <Alert variant={"danger"}>
                    Invalid login provided! Please try again.
                </Alert>
            )
        }
        return (
            <div>
                <Navigation/>
                <Container className={"mt-3"}>
                    <Row>
                        <Col style={{maxWidth: "500px", marginLeft: "auto", marginRight: "auto"}}>
                            <Card style={{width: '100%'}}>
                                <Card.Header as="h2">Login</Card.Header>
                                <Card.Body>
                                    {errorBanner}
                                    <Form onSubmit={this.handleSubmit}>
                                        <Form.Group controlId="formVolunteerName">
                                            <Form.Label>Name</Form.Label>
                                            <UserDropdown handleInputChange={this.handleInputChange} adminOnly={true}/>
                                            <Form.Text className="text-muted">
                                                Start by typing your name and selecting it from the dropdown.
                                            </Form.Text>
                                        </Form.Group>
                                        <Form.Group controlId="formBasicPassword">
                                            <Form.Label>Password</Form.Label>
                                            <Form.Control type="password" placeholder="Password" name="password"
                                                          onChange={this.handleInputChange}/>
                                            <Form.Text className="text-muted">
                                                If you forgot this, someone from Operations will need to reset it.
                                            </Form.Text>
                                        </Form.Group>
                                        <Button variant="primary" type="submit">
                                            Submit
                                        </Button>
                                    </Form>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </Container>
            </div>
        )
    }
}