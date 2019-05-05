import React, { Component } from 'react';
import Container from 'react-bootstrap/Container';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/Row';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Navigation from './Navigation';
import UserDropdown from './UserDropdown';

export default class Home extends Component {
    render() {
       return (
           <div>
                <Navigation/>
                <Container className={"mt-3"}>
                    <Row>
                        <Col xl>
                        <Card style={{ width: '100%' }}>
                            <Card.Body>
                                <Form>
                                    <Form.Group controlId="formVolunteerName">
                                        <Form.Label>Lets start with your name:</Form.Label>
                                        <UserDropdown/>
                                        <Form.Text className="text-muted">
                                            Being to type your name and select it from the dropdown.
                                        </Form.Text>
                                    </Form.Group>
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
