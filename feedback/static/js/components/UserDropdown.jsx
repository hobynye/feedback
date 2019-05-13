import React, {Component} from 'react';
import {Dropdown} from 'semantic-ui-react'

export default class UserDropdown extends Component {
    componentWillMount() {
        this.setState({
            isFetching: true,
            search: true,
            value: "",
            options: [],
        });
        this.fetchOptions();
    }

    handleChange = (e, {value}) => {
        this.setState({value});
        this.props.handleInputChange({target: {value: value, name: "volunteer_id"}});
    };

    fetchOptions = () => {
        let adminOnlyQuery = "";
        this.setState({isFetching: true});
        if (this.props.adminOnly === true) {
            adminOnlyQuery = "?admin=true"
        }
        setTimeout(() => {
            let formattedList = [];
            fetch("/api/users" + adminOnlyQuery)
                .then(response => response.json())
                .then((jsonData) => {
                    const volunteers = jsonData["volunteers"];
                    const arrayLength = volunteers.length;
                    for (let i = 0; i < arrayLength; i++) {
                        formattedList.push(
                            {
                                key: volunteers[i]["name"],
                                text: volunteers[i]["name"],
                                value: volunteers[i]["id"]
                            }
                        )
                    }
                    this.setState({isFetching: false, options: formattedList});
                }).catch((error) => {
                // handle your errors here
                console.error(error)
            });
        })
    };

    render() {
        const {options, isFetching, search, value} = this.state;
        return (
            <Dropdown
                fluid
                selection
                search={search}
                options={options}
                value={value}
                placeholder="Hugh O'Brian"
                onChange={this.handleChange}
                loading={isFetching}
            />)
    }
};