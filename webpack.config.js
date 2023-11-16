module.exports = {
    entry: './main/static/main/javascript/ethereumProvider.js', // Replace with the path to your master.js file
    output: {
        filename: 'bundle.js', // Output bundle file name
        path: __dirname + '/main/static/main/javascript', // Output directory
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env'],
                    },
                },
            },
        ],
    },
};
