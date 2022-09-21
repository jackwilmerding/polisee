<h1 align="center">PoliSee</h1>
<p align="center">PoliSee is a 3D graph representation of congressional cosponsorship data from <a href="https://api.congress.gov/">api.congress.gov</a></p>

## Usage

All installation options require an environment variable file named `.env` in the root directory of the project. The file should contain your MongoDB URI.

```sh
#.env
MONGO_URI=<your-mongo-uri>
```

### Option A: Development

This is a quicker solution that is better for updating the UI. First, start the server from the project's root directory

```sh
# in /
npm i
npm start
```

In another terminal, start the vite dev server. This will proxy all requests to port 3000 where the API is running.

```sh
# in /client
npm i
npm run dev
```

A link should be available in the terminal where you just ran `npm run dev`

### Option B: Production

This option is slower but is more optimized. This is what the live site uses. Build the full static site:

```sh
# in /client
npm i
npm run build
```

This will build the site to the `client/dist` folder. Now run the main server, which will serve this site in addition to the API:

```sh
# in /
npm i
npm start
```
