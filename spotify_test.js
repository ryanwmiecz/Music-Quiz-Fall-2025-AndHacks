// Save this as: spotify_test.js (ES Module version)
import https from 'https';
import { URLSearchParams } from 'url';

class SpotifyPlaylistExtractor {
    constructor(clientId, clientSecret) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.accessToken = null;
        this.tokenExpiry = null;
    }

    async getAccessToken() {
        if (this.accessToken && this.tokenExpiry && new Date() < this.tokenExpiry) {
            return this.accessToken;
        }

        return new Promise((resolve, reject) => {
            const postData = new URLSearchParams({
                'grant_type': 'client_credentials',
                'client_id': this.clientId,
                'client_secret': this.clientSecret
            }).toString();

            const options = {
                hostname: 'accounts.spotify.com',
                port: 443,
                path: '/api/token',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': Buffer.byteLength(postData)
                }
            };

            const req = https.request(options, (res) => {
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    try {
                        const response = JSON.parse(data);
                        
                        if (res.statusCode === 200) {
                            this.accessToken = response.access_token;
                            this.tokenExpiry = new Date(Date.now() + (response.expires_in - 300) * 1000);
                            console.log('✅ Token acquired successfully!');
                            resolve(this.accessToken);
                        } else {
                            console.error('❌ Token error:', response);
                            reject(new Error(`Token error: ${response.error_description || response.error}`));
                        }
                    } catch (error) {
                        console.error('❌ Parse error:', error);
                        reject(error);
                    }
                });
            });

            req.on('error', (error) => {
                console.error('❌ Request error:', error);
                reject(error);
            });

            req.write(postData);
            req.end();
        });
    }

    extractPlaylistId(playlistUrl) {
        const match = playlistUrl.match(/playlist\/([a-zA-Z0-9]+)/);
        return match ? match[1] : playlistUrl;
    }

    async getSongs(playlistUrl) {
        const token = await this.getAccessToken();
        if (!token) {
            throw new Error('Could not get access token');
        }

        const playlistId = this.extractPlaylistId(playlistUrl);
        console.log(`🔍 Getting songs from playlist ID: ${playlistId}`);

        return new Promise((resolve, reject) => {
            const options = {
                hostname: 'api.spotify.com',
                port: 443,
                path: `/v1/playlists/${playlistId}/tracks`,
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            };

            const req = https.request(options, (res) => {
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    try {
                        if (res.statusCode !== 200) {
                            console.error(`❌ API Error ${res.statusCode}:`, data);
                            reject(new Error(`API Error: ${res.statusCode}`));
                            return;
                        }

                        const response = JSON.parse(data);
                        const songsDict = {};

                        response.items.forEach((item, index) => {
                            const track = item.track;
                            if (track) {
                                songsDict[index + 1] = {
                                    name: track.name,
                                    artist: track.artists[0].name,
                                    preview_url: track.preview_url
                                };
                            }
                        });

                        resolve(songsDict);
                    } catch (error) {
                        console.error('❌ Parse error:', error);
                        reject(error);
                    }
                });
            });

            req.on('error', (error) => {
                console.error('❌ Request error:', error);
                reject(error);
            });

            req.end();
        });
    }

    randomSong(songsDict) {
        const keys = Object.keys(songsDict);
        if (keys.length === 0) {
            console.log('❌ No songs available!');
            return null;
        }

        const randomKey = keys[Math.floor(Math.random() * keys.length)];
        const selectedSong = songsDict[randomKey];

        return {
            songNumber: randomKey,
            song: selectedSong
        };
    }
}

// Main function - asks user for playlist URL
async function main() {
    console.log('🎵 SPOTIFY PLAYLIST EXTRACTOR');
    console.log('='.repeat(40));

    // Setup readline for user input
    const readline = await import('readline');
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const askQuestion = (question) => {
        return new Promise((resolve) => {
            rl.question(question, (answer) => {
                resolve(answer);
            });
        });
    };

    // Your credentials
    const extractor = new SpotifyPlaylistExtractor(
        "018027c623224686a56a98aedf98f7c4", // Your Client ID
        "0068d7bd972b454da81de17f6e3193d6"  // Your Client Secret
    );

    try {
        // Get playlist URL from user
        const playlistUrl = await askQuestion('Enter Spotify playlist URL: ');
        
        if (!playlistUrl.trim()) {
            console.log('❌ No playlist URL provided!');
            rl.close();
            return;
        }

        console.log('\n🔄 Getting songs from playlist...');
        
        // Get songs as dictionary
        const songs = await extractor.getSongs(playlistUrl);

        if (Object.keys(songs).length > 0) {
            console.log(`\n🎵 Found ${Object.keys(songs).length} songs and added to dictionary!`);
            console.log('-'.repeat(50));
            
            // Display all songs
            for (const [key, song] of Object.entries(songs)) {
                console.log(`${key}. ${song.name} - ${song.artist}`);
            }
            
            // Ask to randomly select
            console.log('\n' + '='.repeat(50));
            const choice = await askQuestion('Randomly select a song? (y/n): ');
            
            if (choice.toLowerCase() === 'y') {
                const result = extractor.randomSong(songs);
                if (result) {
                    console.log(`\n🎲 RANDOMLY SELECTED SONG:`);
                    console.log(`#${result.songNumber}: ${result.song.name} - ${result.song.artist}`);
                    
                    if (result.song.preview_url) {
                        console.log(`🎧 Preview: ${result.song.preview_url}`);
                    } else {
                        console.log(`❌ No preview available`);
                    }
                }
            }
            
        } else {
            console.log('❌ No songs found!');
        }

    } catch (error) {
        console.error('❌ Error:', error.message);
        console.log('\n🔧 Troubleshooting:');
        console.log('   - Make sure the playlist URL is correct');
        console.log('   - Check that the playlist is public');
        console.log('   - Verify your internet connection');
    } finally {
        rl.close();
    }
}

// Run the main function
main();

export default SpotifyPlaylistExtractor;