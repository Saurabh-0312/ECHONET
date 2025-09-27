import express from 'express';
import { nameToAddress, addressToName } from '../controller/ensController.js';

const Router = express.Router();

Router.post('/resolve', nameToAddress);
Router.post('/reverse', addressToName);

export default Router;  