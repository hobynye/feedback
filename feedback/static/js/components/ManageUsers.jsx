import React, { Component } from 'react';
import Navigation from './Navigation'
import Container from 'react-bootstrap/Container'
import Card from 'react-bootstrap/Card'
import Col from 'react-bootstrap/Col'
import Row from 'react-bootstrap/Row'

export default class ManageUsers extends Component {
    render() {
       return (
           <div>
                <Navigation/>
                <Container className={"mt-3"}>
                    <Row>
                        <Col xl>
                        <Card style={{ width: '100%' }}>
                            <Card.Body>
                                <p>Manage Users</p>
                            </Card.Body>
                        </Card>
                        </Col>
                    </Row>
                </Container>
           </div>
       )
    }
}
