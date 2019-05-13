import React, {Component} from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Nav from 'react-bootstrap/Nav';

export default class Navigation extends Component {
    render() {
        let user;
        if (this.props.currentUser) {
            user = (
                <NavDropdown title={this.props.currentUser} id="basic-nav-dropdown">
                    <NavDropdown.Item href="/api/logout">Logout</NavDropdown.Item>
                </NavDropdown>
            )
        }
        return (
            <div>
                <Navbar expand="md" bg="primary" variant="dark" sticky="top">
                    <Container>
                        <Navbar.Brand href="#home">
                            <img
                                alt="HOBY Logo"
                                src="/public/img/hoby-logo.svg"
                                height="25"
                                className="d-inline-block align-top"
                            />
                            <div id="title">Feedback</div>
                            <Nav/>
                        </Navbar.Brand>
                        <Navbar.Toggle aria-controls="responsive-navbar-nav"/>
                        <Navbar.Collapse id="responsive-navbar-nav" className="justify-content-end">
                            <Nav>
                                <NavDropdown title="Operations" id="basic-nav-dropdown">
                                    <NavDropdown.Item href="#results">View Results</NavDropdown.Item>
                                    <NavDropdown.Item href="#users">Manage Users</NavDropdown.Item>
                                </NavDropdown>
                                {user}
                            </Nav>
                        </Navbar.Collapse>
                    </Container>
                </Navbar>
            </div>
        )
    }
}
