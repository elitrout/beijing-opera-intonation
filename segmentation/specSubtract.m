% Obtain clean singing voice by subtracting background music from mix.

clear
close all

[mix,fs] = audioread('~/Downloads/1-02yutangchun.wav');
[back,fs] = audioread('~/Downloads/1-08yutangchun_back.wav');
x = mix(:,1);                                % Select a channel
L = size(x,1);                                  % Audio length
b = back(:,1);
b = b(1:L,:);

%blockLen = fs*5;                                % Block length
blockLen = L;
blockNum = ceil(L/blockLen);                    % Block number
x = [x', zeros(1, blockNum*blockLen-L)]';       % Zero padding
b = [b', zeros(1, blockNum*blockLen-L)]';

N = 1024;                                       % N of FFT
N2 = ceil((N+1)/2);                             % Half N
H = floor(N/2);                                 % Hop size
F = ceil((blockLen-N)/H);                       % No. of frames

% for i=1:blockNum
for i=1:1    % use the first block for now
    blockm = x((i-1)*blockLen+1 : i*blockLen);
    blockb = b((i-1)*blockLen+1 : i*blockLen);
    Xm = spectrogram(blockm,hann(N),N-H,N,fs);        % STFT
    Mm = abs(Xm);                                     % Spectrum Magnitude
    Pm = unwrap(angle(Xm));                           % Spectrum Phase
    Xb = spectrogram(blockb,hann(N),N-H,N,fs);        % STFT
    Mb = abs(Xb);                                     % Spectrum Magnitude
    Pb = unwrap(angle(Xb));                           % Spectrum
                                                      % Phase
end

%% Reconstruct audio from basis

% Overlap-add synthesis
R = Mm-Mb;                             % Magnitude
R(R<eps) = eps;
Z = R .* exp(1i * Pm);                  % Reconstructed complex number
Z = [Z; conj(Z(end-1:-1:2, :))];       % Complete the spectrogram
xr = zeros(1, N+(F-1)*H);              % Initialize reconstructed signal
sw = blackmanharris(N, 'periodic');    % Synthesis window
for k = 1:F
    xi = ifft(Z(:,k), 'symmetric');
    % overlap-add
    xr((k-1)*H+1 : (k-1)*H+N) = xr((k-1)*H+1 : (k-1)*H+N) + (xi.*sw)';
end
xr = xr.*H/sum(sw.^2);      % Normalization

outputAudio = './data/SpecSub.wav';
wavwrite(xr,fs,outputAudio);

%% Plot results
% plot original spectrogram
figure(1);
subplot(2,1,1);
imagesc((1:F)*H/fs, fs/N*(1:N2), log(Mm)); % plot the log spectrum
set(gca,'YDir', 'normal'); % flip the Y Axis so lower frequencies
                           % are at the bottom
title 'Original Spectrogram';
xlabel('Time (s)');
ylabel('Frequency (Hz)');

subplot(2,1,2);
imagesc((1:F)*H/fs, fs/N*(1:N2), log(Mb)); % plot the log spectrum
set(gca,'YDir', 'normal'); % flip the Y Axis so lower frequencies
                           % are at the bottom
title 'Original Spectrogram';
xlabel('Time (s)');
ylabel('Frequency (Hz)');

% plot reconstruction of all basis
figure(2);
imagesc((1:F)*H/fs, fs/N*(1:N2), log(R)); % plot the log spectrum
set(gca,'YDir', 'normal'); % flip the Y Axis so lower frequencies
                           % are at the bottom
title(['Reconstruction']);
xlabel('Time (s)');
ylabel('Frequency (Hz)');
