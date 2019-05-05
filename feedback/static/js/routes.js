import React from 'react';
import { HashRouter, Route, hashHistory } from 'react-router-dom';
import Home from './components/Home';
import Results from './components/Results'
import ManageUsers from "./components/ManageUsers";

export default (
    <HashRouter history={hashHistory}>
     <div>
      <Route exact path='/' component={Home} />
      <Route path='/home' component={Home} />
      <Route path='/results' component={Results} />
      <Route path='/users' component={ManageUsers} />
     </div>
    </HashRouter>
);
