import { useEffect, useState } from 'react';
import { Box, Text, VStack, Heading, List, ListItem, SimpleGrid, useTheme, Button, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, useDisclosure, Flex } from '@chakra-ui/react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

function Dashboard() {
  const [userData, setUserData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setLoading(true);
        // Extract access token from URL query parameters
        const params = new URLSearchParams(window.location.search);
        const accessToken = params.get('access_token');

        if (!accessToken) {
          setError('Access token not found.');
          setLoading(false);
          return;
        }

        // Fetch data from backend endpoint
        // Use the VITE_API_URL environment variable
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/user/data?access_token=${accessToken}`);

        if (!response.ok) {
          const errorData = await response.json();
          // Construct a more informative error message if detail is available
          const errorMessage = errorData.detail ? `Error fetching data: ${response.status} ${response.statusText} - ${errorData.detail}` : `Error fetching data: ${response.status} ${response.statusText}`; 
          throw new Error(errorMessage);
        }

        const data = await response.json();
        setUserData(data);

      } catch (err: any) {
        console.error('Error fetching user data:', err);
        // Assuming the error object has a message property
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []); // Empty dependency array means this effect runs once on mount

  // Function to process liked songs data for the bar chart (count by date)
  const processLikedSongsDataByDate = (data: any) => {
    if (!data || !data.spotify_liked_songs) return [];

    const likedSongsByDate: { [key: string]: number } = {};

    // Sort data by added_at before processing to ensure correct date order
    const sortedLikedSongs = data.spotify_liked_songs.sort((a: any, b: any) => new Date(a.added_at).getTime() - new Date(b.added_at).getTime());

    sortedLikedSongs.forEach((song: any) => {
      // Assuming 'added_at' is in a format that includes date (e.g., ISO 8601 string)
      const date = new Date(song.added_at).toLocaleDateString(); // Get date part
      likedSongsByDate[date] = (likedSongsByDate[date] || 0) + 1;
    });

    // Convert the object to an array of objects for Recharts
    return Object.keys(likedSongsByDate).map(date => ({
      date,
      count: likedSongsByDate[date],
    }));
  };

   // Function to process liked songs data for the pie chart (breakdown by artist)
   const processLikedSongsDataByArtist = (data: any) => {
    if (!data || !data.spotify_liked_songs) return [];

    const likedSongsByArtist: { [key: string]: number } = {};

    data.spotify_liked_songs.forEach((song: any) => {
      const artistName = song.artist_name || 'Unknown Artist';
      likedSongsByArtist[artistName] = (likedSongsByArtist[artistName] || 0) + 1;
    });

    // Convert the object to an array of objects for Recharts
    return Object.keys(likedSongsByArtist).map(artist_name => ({
      artist_name,
      count: likedSongsByArtist[artist_name],
    }));
  };

  // Function to process top artists data for the bar chart (popularity)
  const processTopArtistsData = (data: any) => {
    if (!data || !data.spotify_top_artists) return [];

    // Sort artists by popularity in descending order
    const sortedArtists = data.spotify_top_artists.sort((a: any, b: any) => b.popularity - a.popularity);

    return sortedArtists.map((artist: any) => ({
      artist_name: artist.artist_name,
      popularity: artist.popularity,
    }));
  };

  // Function to process recently played data for listing and remove duplicates
  const processRecentlyPlayedData = (data: any) => {
      if (!data || !data.spotify_recently_played) return [];

      const uniqueTracks = new Map();

      // Iterate through tracks in reverse to keep the most recent version of a track
      // before adding to the map.
      for (let i = data.spotify_recently_played.length - 1; i >= 0; i--) {
          const track = data.spotify_recently_played[i];
          if (!uniqueTracks.has(track.track_id)) {
              uniqueTracks.set(track.track_id, track);
          }
      }

      // Convert map values back to an array and sort by played_at descending
      const sortedUniqueTracks = Array.from(uniqueTracks.values()).sort((a: any, b: any) => new Date(b.played_at).getTime() - new Date(a.played_at).getTime());

      // Limit to maximum 10 entries
      return sortedUniqueTracks.slice(0, 10);
  };

  // Function to process playlist data for track counts chart
  const processPlaylistTrackCounts = (data: any) => {
      if (!data || !data.spotify_user_playlists) return [];
      return data.spotify_user_playlists.map((playlist: any) => ({
          playlist_name: playlist.playlist_name,
          track_count: playlist.track_count,
      }));
  };

  const likedSongsChartDataByDate = processLikedSongsDataByDate(userData);
  const likedSongsChartDataByArtist = processLikedSongsDataByArtist(userData);
  const topArtistsChartData = processTopArtistsData(userData);
  const recentlyPlayedData = processRecentlyPlayedData(userData);
  const playlistTrackCountsData = processPlaylistTrackCounts(userData);


  // Define colors for the pie chart slices
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28AE5', '#FF66C4', '#66D8A1', '#FF9933', '#66B2FF', '#FFB366'];

  // Chakra UI hook for modal
  const { isOpen, onOpen, onClose } = useDisclosure();

  if (loading) {
    return <Text>Loading user data...</Text>;
  }

  if (error) {
    return <Text color="red.500">Error: {error}</Text>;
  }

  // Render the dashboard content once data is loaded
  return (
    <Box p={8} bg="spotify.black" color="spotify.white" minH="100vh">
      <Flex justify="space-between" align="center" mb={6}>
         <Heading color="spotify.white">User Dashboard</Heading>
         {userData?.spotify_user_profile && (
             <Button onClick={onOpen} colorScheme="spotify" size="sm">
                 View Profile
             </Button>
         )}
      </Flex>

      <VStack spacing={8} align="stretch">

        {/* Liked Songs Over Time Bar Chart */}
        {likedSongsChartDataByDate.length > 0 && (
          <Box>
            <Heading size="md" mb={4}>Liked Songs Over Time</Heading>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={likedSongsChartDataByDate}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Box>
        )}

        {/* Charts in a grid */}
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8}>
            {/* Liked Songs Breakdown by Artist Donut Chart */}
            {likedSongsChartDataByArtist.length > 0 && (
                <Box>
                     <Heading size="md" mb={4}>Liked Songs Breakdown by Artist</Heading>
                     <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={likedSongsChartDataByArtist}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="count"
                                label={({ artist_name, percent }) => `${artist_name} ${(percent * 100).toFixed(0)}%`}
                            >
                                {likedSongsChartDataByArtist.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                     </ResponsiveContainer>
                </Box>
            )}

            {/* Top Artists by Popularity Bar Chart */}
            {topArtistsChartData.length > 0 && (
                <Box>
                     <Heading size="md" mb={4}>Your Top Artists by Popularity</Heading>
                     <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={topArtistsChartData}>
                            <XAxis dataKey="artist_name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="popularity" fill="#82ca9d" />
                        </BarChart>
                     </ResponsiveContainer>
                </Box>
            )}

            {/* MOST LIKED ARTISTS OF YOURS Donut Chart (using liked songs data)*/}
            {likedSongsChartDataByArtist.length > 0 && (
                <Box>
                     <Heading size="md" mb={4}>MOST LIKED ARTISTS OF YOURS</Heading>
                     <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={likedSongsChartDataByArtist}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="count"
                                label={({ artist_name, percent }) => `${artist_name} ${(percent * 100).toFixed(0)}%`}
                            >
                                {likedSongsChartDataByArtist.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                     </ResponsiveContainer>
                </Box>
            )}

             {/* Playlist Track Counts Bar Chart */}
             {playlistTrackCountsData.length > 0 && (
                 <Box>
                      <Heading size="md" mb={4}>Playlist Track Counts</Heading>
                      <ResponsiveContainer width="100%" height={300}>
                         <BarChart data={playlistTrackCountsData}>
                             <XAxis dataKey="playlist_name" />
                             <YAxis />
                             <Tooltip />
                             <Legend />
                             <Bar dataKey="track_count" fill="#ff7300" />
                         </BarChart>
                      </ResponsiveContainer>
                 </Box>
             )}

        </SimpleGrid>

        {/* Recently Played Tracks List */}
        {recentlyPlayedData.length > 0 && (
            <Box>
                <Heading size="md" mb={4}>Recently Played Tracks</Heading>
                <List spacing={2}>
                    {recentlyPlayedData.map((track: any, index: number) => (
                        <ListItem key={index}>
                            <Text>{track.track_name} by {track.artist_name} from {track.album_name}</Text>
                        </ListItem>
                    ))}
                </List>
            </Box>
        )}


        {/* TODO: Add other chart components here */}
      </VStack>
    </Box>
  );
}

export default Dashboard;