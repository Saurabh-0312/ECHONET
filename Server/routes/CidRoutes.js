import express from 'express';
import { getCidData } from '../controller/CidController.js';

const Router = express.Router();

Router.post('/cid', getCidData);

export default Router;