import { Tabs } from 'expo-router';
import { StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={styles.container}>
      <SafeAreaProvider>
        <StatusBar style="light" backgroundColor="#1B4332" />
        <Tabs
          screenOptions={{
            tabBarStyle: styles.tabBar,
            tabBarActiveTintColor: '#40C974',
            tabBarInactiveTintColor: '#6B7280',
            tabBarLabelStyle: styles.tabLabel,
            headerStyle: styles.header,
            headerTintColor: '#FFFFFF',
            headerTitleStyle: styles.headerTitle,
          }}
        >
          <Tabs.Screen
            name="index"
            options={{
              title: 'Home',
              tabBarIcon: ({ color, size }) => (
                <Ionicons name="home" size={size} color={color} />
              ),
              headerTitle: 'ਕਿਸਾਨ ਸਾਥੀ • Kisaan Saathi',
            }}
          />
          <Tabs.Screen
            name="crop"
            options={{
              title: 'Crops',
              tabBarIcon: ({ color, size }) => (
                <Ionicons name="leaf" size={size} color={color} />
              ),
              headerTitle: 'Crop Advisory',
            }}
          />
          <Tabs.Screen
            name="disease"
            options={{
              title: 'Disease',
              tabBarIcon: ({ color, size }) => (
                <Ionicons name="camera" size={size} color={color} />
              ),
              headerTitle: 'Pest & Disease',
            }}
          />
          <Tabs.Screen
            name="weather"
            options={{
              title: 'Weather',
              tabBarIcon: ({ color, size }) => (
                <Ionicons name="partly-sunny" size={size} color={color} />
              ),
              headerTitle: 'Weather & Alerts',
            }}
          />
          <Tabs.Screen
            name="soil"
            options={{
              title: 'Soil',
              tabBarIcon: ({ color, size }) => (
                <Ionicons name="earth" size={size} color={color} />
              ),
              headerTitle: 'Soil & Fertilizer',
            }}
          />
          <Tabs.Screen
            name="market"
            options={{
              title: 'Market',
              tabBarIcon: ({ color, size }) => (
                <Ionicons name="trending-up" size={size} color={color} />
              ),
              headerTitle: 'Market Prices',
            }}
          />
          <Tabs.Screen
            name="diary"
            options={{
              title: 'ਡਾਇਰੀ',
              tabBarIcon: ({ color, size }) => (
                <Ionicons name="book-outline" size={size} color={color} />
              ),
              headerTitle: 'ਖੇਤ ਡਾਇਰੀ • Farm Diary',
            }}
          />
        </Tabs>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  tabBar: {
    backgroundColor: '#111827',
    borderTopColor: '#1F2937',
    height: 60,
    paddingBottom: 8,
    paddingTop: 4,
  },
  tabLabel: {
    fontSize: 10,
    fontWeight: '600',
  },
  header: {
    backgroundColor: '#1B4332',
  },
  headerTitle: {
    fontWeight: '700',
    fontSize: 16,
  },
});
