import React, { Component } from 'react';
import Container from 'react-bootstrap/Container'
import Card from 'react-bootstrap/Card'
import Col from 'react-bootstrap/Col'
import Navigation from './Navigation'

export default class Results extends Component {
    render() {
       return (
           <div>
                <Navigation/>
                <Container className={"mt-3"}>
                    <Row>
                        <Col xl>
                        <Card style={{ width: '100%' }}>
                            <Card.Body>
                                <p>Results</p>
                            </Card.Body>
                        </Card>
                        </Col>
                    </Row>
                </Container>
           </div>
       )
    }
}
