import React, {Component} from 'react';
import Container from 'react-bootstrap/Container'
import Card from 'react-bootstrap/Card'
import Col from 'react-bootstrap/Col'
import Row from 'react-bootstrap/Row'
import Navigation from './Navigation'

const FeedbackItem = ({feedback}) => (
    <>
        {feedback.map(feedback => (
            <Card bg={feedback.severity} text="white" style={{width: '100%', marginBottom: "15px"}}>
                <Card.Header>
                    <strong>{feedback.author}</strong>
                    <p style={{display: "block"}}>{feedback.role} {feedback.color} {feedback.letter} - {feedback.submitted}</p>
                </Card.Header>
                <Card.Body>
                    <Card.Title>{feedback.body}</Card.Title>
                </Card.Body>
            </Card>
        ))}
    </>
);

export default class Results extends Component {
    constructor(props) {
        super(props);
        this.state = {
            user: "",
            loading: true,
            feedback: []
        }
    }

    componentWillMount() {

        fetch("/api/user/self")
            .then((response) => {
                if (response.status == 405) {
                    window.location.replace("/#/login?next=/#/results");
                }
                return response
            }).then((response) => response.json())
            .then((jsonData) => {
                this.setState({
                    user: jsonData.current_user.name
                });
                this.fetchFeedback();
            })
    }

    componentDidMount() {
        this.interval = setInterval(() => {this.fetchFeedback()}, 30000);
    }

    componentWillUnmount() {
        clearInterval(this.interval);
    }

    fetchFeedback = () => {
        this.setState({loading: true});
        let feedbackArray = [];
        let sevMapping = {
            Red: "danger",
            Yellow: "warning",
            Green: "success"
        };
        setTimeout(() => {
            fetch("/api/feedback?qty=100")
                .then(response => response.json())
                .then((jsonData) => {
                    const feedback = jsonData["results"];
                    const arrayLength = feedback.length;
                    for (let i = 0; i < arrayLength; i++) {
                        let timestamp = new Date(0);
                        timestamp.setUTCSeconds(feedback[i]["submitted"]);
                        feedbackArray.push(
                            {
                                key: feedback[i]["id"],
                                author: feedback[i]["author"],
                                role: feedback[i]["role"],
                                color: feedback[i]["color"],
                                letter: feedback[i]["letter"],
                                severity: sevMapping[feedback[i]["severity"]],
                                body: feedback[i]["body"],
                                submitted: timestamp.toString()
                            }
                        )
                    }
                })
                .then(() => {
                    this.setState({loading: false, feedback: feedbackArray});
                })
                .catch((error) => {
                    // handle your errors here
                    console.error(error)
                });
        })
    };

    render() {
        console.log(this.state.feedback);
        return (
            <div>
                <Navigation currentUser={this.state.user}/>
                <Container className={"mt-3"}>
                    <Row>
                        <Col xl>
                            <FeedbackItem feedback={this.state.feedback}/>
                        </Col>
                    </Row>
                </Container>
            </div>
        )
    }
}
