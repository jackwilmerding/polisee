<h1 align="center">Poli See</h1>
<p align="center">Poli See is a 3D graph of representation of congressional voting data from <a href="https://api.congress.gov/">api.congress.gov</a></p>

## Usage

All installation options require an environment variable file named `.env` in the root directory of the project. The file should contain your MongoDB URI.

```sh
#.env
MONGO_URI=<your-mongo-uri>
```

### Option A: Development

First, start the server from the project's root directory

```sh
npm i
npm start
```

In another terminal, start the vite dev server. This will proxy all requests to port 3000 where the API is running.

```sh
npm i
npm run dev
```

A link should be available in the terminal where you just ran `npm run dev`
