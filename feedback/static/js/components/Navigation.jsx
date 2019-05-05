import React, { Component } from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Nav from 'react-bootstrap/Nav';

export default class Navigation extends Component {
    render() {
       return (
           <div>
            <Navbar expand="md" bg="white" variant="light" sticky="top">
                <Container>
                    <Navbar.Brand href="#home">
                      <img
                        alt="HOBY Logo"
                        src="/public/img/logo.png"
                        height="25"
                        className="d-inline-block align-top"
                      />
                      {' Feedback'}
                      <Nav/>
                    </Navbar.Brand>
                    <Navbar.Toggle aria-controls="responsive-navbar-nav" />
                    <Navbar.Collapse id="responsive-navbar-nav" className="justify-content-end">
                        <NavDropdown title="Operations" id="basic-nav-dropdown">
                            <NavDropdown.Item href="#results">View Results</NavDropdown.Item>
                            <NavDropdown.Item href="#users">Manage Users</NavDropdown.Item>
                        </NavDropdown>
                    </Navbar.Collapse>
                </Container>
              </Navbar>

           </div>
       )
    }
}
